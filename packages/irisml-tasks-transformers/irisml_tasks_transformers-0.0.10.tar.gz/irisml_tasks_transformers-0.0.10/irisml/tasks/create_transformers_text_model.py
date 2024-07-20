import dataclasses
import logging
from typing import List, Optional, Tuple
import torch
import transformers
import irisml.core
from irisml.tasks.create_transformers_model import with_azure_directory

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Create a text-generation model using transformers library.

    Config:
        name (str): Name of the model to load. See https://huggingface.co/models for a list of available models.
        azure_blob_container_url (str): Azure blob container URL to download the model from.
        azure_blob_path_prefix (str): Azure blob path prefix to download the model from.
    """
    VERSION = '0.2.1'

    @dataclasses.dataclass
    class Config:
        name: str
        azure_blob_container_url: Optional[str] = None
        azure_blob_path_prefix: Optional[str] = None

    @dataclasses.dataclass
    class Outputs:
        model: torch.nn.Module

    def execute(self, inputs):
        self._check_config()

        if 'blip2' in self.config.name:
            model_class = transformers.Blip2ForConditionalGeneration
        else:
            model_class = transformers.AutoModel

        if self.config.azure_blob_container_url:
            prefix = (self.config.name + '/') if not self.config.azure_blob_path_prefix else f'{self.config.azure_blob_path_prefix}/{self.config.name}/'
            with with_azure_directory(self.config.azure_blob_container_url, prefix) as temp_dir:
                model = model_class.from_pretrained(temp_dir)
                processor = transformers.AutoProcessor.from_pretrained(temp_dir)
        else:
            model = model_class.from_pretrained(self.config.name)
            processor = transformers.AutoProcessor.from_pretrained(self.config.name)

        if not isinstance(model, transformers.Blip2PreTrainedModel):
            raise RuntimeError(f"The model type {type(model)} is not supported. Please submit a pull request.")

        return self.Outputs(TextGenerationModel(model, processor))

    def dry_run(self, inputs):
        self._check_config()
        return self.Outputs(FakeModel())

    def _check_config(self):
        if not self.config.name:
            raise ValueError("name is required")

        if not self.config.azure_blob_container_url and self.config.azure_blob_path_prefix:
            raise ValueError("azure_blob_path_prefix requires azure_blob_container_url")


class TextGenerationModel(torch.nn.Module):
    """Model that generates text.

    Input: [(text, [image_tensor, ...]), ...]
    Output: [text, ...]

    image_tensor is a tensor of shape (C, H, W) and values in [0, 1].
    """
    def __init__(self, model, processor):
        super().__init__()
        self._model = model
        self._processor = processor
        self._dtype = torch.float16
        self._device = torch.device('cpu')
        self._model.to(self._dtype)

    def forward(self, inputs: List[Tuple[str, List[torch.Tensor]]]) -> List[str]:
        results = []
        for text, images in inputs:
            inputs = self._processor(images=torch.stack(images) * 255, text=text, return_tensors='pt', padding=True).to(self._device, self._dtype)
            generated_ids = self._model.generate(**inputs)
            generated_text = self._processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
            logger.debug(f"Generated text: {repr(generated_text)}")
            results.append(generated_text)
        return results

    def to(self, device, *args, **kwargs):
        if not isinstance(device, torch.device):
            raise NotImplementedError("Only torch.device is supported")
        self._device = device
        return super().to(device, *args, **kwargs)

    def state_dict(self):
        return self._model.state_dict()

    def load_state_dict(self, *args, **kwargs):
        return self._model.load_state_dict(*args, **kwargs)


class FakeModel(torch.nn.Module):
    def forward(self, inputs: List[Tuple[str, List[torch.Tensor]]]) -> List[str]:
        return [''] * len(inputs)
