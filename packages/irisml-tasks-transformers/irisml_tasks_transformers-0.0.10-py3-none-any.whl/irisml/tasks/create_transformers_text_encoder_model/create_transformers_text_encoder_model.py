import dataclasses
import json
import logging
import pathlib
import torch
import transformers
import irisml.core

logger = logging.getLogger(__name__)


CONFIG_FILES = {'openai/clip-vit-base-patch32': 'openai_clip_vit_base_patch32.json'}


class Task(irisml.core.TaskBase):
    """Create a text encoder model using transformers library.

    The model has the following interface:
    - Inputs: A tuple of two tensors: input_ids and attention_mask.
    - Outputs: A tensor of shape (batch_size, feature_size) containing the feature vectors.

    Config:
        name (str): The name of the model to create. Supported models are: 'openai/clip-vit-base-patch32'.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Config:
        name: str

    @dataclasses.dataclass
    class Outputs:
        model: torch.nn.Module

    def execute(self, inputs):
        if self.config.name not in CONFIG_FILES:
            raise ValueError(f"Model {self.config.name} is not supported.")

        config_path = pathlib.Path(__file__).parent / 'resources' / CONFIG_FILES[self.config.name]
        config = json.loads(config_path.read_text())

        model = None
        if config.get('model_type') == 'clip':
            c = transformers.CLIPTextConfig.from_pretrained(config_path)
            transformers_model = transformers.CLIPTextModel(c)
            model = TextEncoderModel(transformers_model)

        if model is None:
            raise ValueError(f"Model {self.config.name} is not supported.")

        return self.Outputs(model)


class TextEncoderModel(torch.nn.Module):
    def __init__(self, transformers_model):
        super().__init__()
        self._model = transformers_model

    def prediction_step(self, inputs: tuple[torch.Tensor, torch.Tensor]):
        input_ids, attention_mask = inputs
        assert input_ids.shape == attention_mask.shape, f"Expected input_ids and attention_mask to have the same shape, got {input_ids.shape} and {attention_mask.shape}"
        assert input_ids.ndim == 2 and attention_mask.ndim == 2, f"Expected 2D tensors, got {input_ids.shape} and {attention_mask.shape}"

        outputs = self._model(input_ids=input_ids, attention_mask=attention_mask, return_dict=True)
        feature_vectors = outputs.pooler_output

        assert isinstance(feature_vectors, torch.Tensor)
        assert len(feature_vectors) == len(input_ids)
        assert feature_vectors.ndim == 2

        return feature_vectors

    def state_dict(self):
        return self._model.state_dict()

    def load_state_dict(self, *args, **kwargs):
        self._model.load_state_dict(*args, **kwargs)
