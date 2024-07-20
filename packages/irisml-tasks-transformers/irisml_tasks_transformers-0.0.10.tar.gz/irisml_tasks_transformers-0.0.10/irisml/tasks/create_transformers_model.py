import contextlib
import dataclasses
import logging
import pathlib
import tempfile
from typing import Optional
from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient
import torch.nn
import transformers
import irisml.core
from irisml.tasks.make_image_text_contrastive_model import ImageTextContrastiveModel

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Create a model using transformers library.

    Supported models:
        - CLIP
        - Bert

    Config:
        name (str): Name of the model to load. See https://huggingface.co/models for a list of available models.
        pretrained (bool): Whether to load the model in pretrained mode.
        azure_blob_container_url (str): Azure blob container URL to download the model from.
        azure_blob_path_prefix (str): Azure blob path prefix to download the model from.
    """
    VERSION = '0.3.1'

    @dataclasses.dataclass
    class Config:
        name: str
        pretrained: bool = False
        azure_blob_container_url: Optional[str] = None
        azure_blob_path_prefix: Optional[str] = None
        filepath: Optional[pathlib.Path] = None

    @dataclasses.dataclass
    class Outputs:
        model: torch.nn.Module

    def execute(self, inputs):
        return self.Outputs(self._create_model(self.config.name, self.config.pretrained, self.config.azure_blob_container_url, self.config.azure_blob_path_prefix, self.config.filepath))

    def dry_run(self, inputs):
        return self.Outputs(self._create_model(self.config.name, False, None, None, None))

    @staticmethod
    def _create_model(name, pretrained, azure_blob_container_url, azure_blob_path_prefix, local_filepath):
        if not name:
            raise ValueError("name is required")

        if name.endswith('/'):
            raise ValueError("name should not end with /")

        if pretrained and azure_blob_container_url:
            raise ValueError("pretrained and azure_blob_container_url are mutually exclusive")

        if not azure_blob_container_url and azure_blob_path_prefix:
            raise ValueError("azure_blob_path_prefix requires azure_blob_container_url")

        if local_filepath:
            transformers_model = transformers.AutoModel.from_pretrained(local_filepath)
        elif azure_blob_container_url:
            prefix = (name + '/') if not azure_blob_path_prefix else f'{azure_blob_path_prefix}/{name}/'
            with with_azure_directory(azure_blob_container_url, prefix) as temp_dir:
                transformers_model = transformers.AutoModel.from_pretrained(temp_dir)
        elif pretrained:
            transformers_model = transformers.AutoModel.from_pretrained(name)
        else:
            transformers_config = transformers.AutoConfig.from_pretrained(name)
            transformers_model = transformers.AutoModel.from_config(transformers_config)

        if isinstance(transformers_model, transformers.CLIPModel):
            model = ImageTextContrastiveModel(PoolerOutputExtractor(ImageInputPreprocessor(transformers_model.vision_model)), PoolerOutputExtractor(transformers_model.text_model),
                                              transformers_model.visual_projection, transformers_model.text_projection,
                                              'clip', float(transformers_model.logit_scale))
        elif isinstance(transformers_model, transformers.BertModel):
            model = transformers_model  # Return the model as-is
        else:
            raise RuntimeError(f"The model type {type(transformers_model)} is not supported. Please submit a pull request.")

        return model


@contextlib.contextmanager
def with_azure_directory(blob_container_url, blob_prefix):
    assert blob_prefix.endswith('/')
    container_client = ContainerClient.from_container_url(blob_container_url, credential=DefaultAzureCredential())
    blob_names = list(container_client.list_blob_names(name_starts_with=blob_prefix))
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = pathlib.Path(temp_dir)
        for blob_name in blob_names:
            filepath = temp_dir / blob_name[len(blob_prefix):]
            blob_client = container_client.get_blob_client(blob_name)
            logger.info(f"Downloading {blob_name} to {filepath}")
            filepath.write_bytes(blob_client.download_blob().readall())

        yield temp_dir


class ImageInputPreprocessor(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self._model = model

        # TODO: Load the mean/std from the model
        # Note that those mean/std is different from the one used in ImageNet models
        self.register_buffer('mean_value', torch.Tensor([0.481, 0.458, 0.408]).view(3, 1, 1))
        self.register_buffer('std_value', torch.Tensor([0.269, 0.261, 0.276]).view(3, 1, 1))
        logger.info("Using mean=[0.481, 0.458, 0.408] and std=[0.269, 0.261, 0.276] for image preprocessing")

    def forward(self, inputs):
        return self._model((inputs - self.mean_value) / self.std_value)

    def state_dict(self):
        return self._model.state_dict()

    def load_state_dict(self, *args, **kwargs):
        return self._model.load_state_dict(*args, **kwargs)


class PoolerOutputExtractor(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self._model = model

    def forward(self, inputs):
        if isinstance(inputs, tuple) and len(inputs) == 2:
            result = self._model(input_ids=inputs[0], attention_mask=inputs[1])
        else:
            result = self._model(inputs)
        return result.pooler_output

    def state_dict(self):
        return self._model.state_dict()

    def load_state_dict(self, *args, **kwargs):
        return self._model.load_state_dict(*args, **kwargs)
