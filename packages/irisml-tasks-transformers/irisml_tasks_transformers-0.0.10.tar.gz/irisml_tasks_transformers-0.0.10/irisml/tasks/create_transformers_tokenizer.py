import dataclasses
import logging
import pathlib
import typing

from transformers import AutoTokenizer
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Create a Tokenizer using transformers library.

    Config:
        name (str): Name of the tokenizer to load. Either name or local_filepath is required.
        local_filepath (pathlib.Path): Local path to the tokenizer file.
    """
    VERSION = '0.2.0'

    @dataclasses.dataclass
    class Config:
        name: str | None = None
        local_filepath: pathlib.Path | None = None

    @dataclasses.dataclass
    class Outputs:
        tokenizer: typing.Callable

    def execute(self, inputs):
        if not self.config.name and not self.config.local_filepath:
            raise ValueError("name or local_filepath is required")

        if self.config.name:
            logger.info(f"Loading tokenizer {self.config.name} from huggingface server.")
            tokenizer = AutoTokenizer.from_pretrained(self.config.name)
        else:
            logger.info(f"Loading tokenizer from local file {self.config.local_filepath}")
            tokenizer = AutoTokenizer.from_pretrained(self.config.local_filepath)

        return self.Outputs(Tokenizer(tokenizer))

    def dry_run(self, inputs):
        return self.execute(inputs)


class Tokenizer:
    def __init__(self, tokenizer):
        self._tokenizer = tokenizer

    def __call__(self, inputs):
        outputs = self._tokenizer(inputs, return_tensors='pt', padding='max_length', max_length=77)
        return outputs['input_ids'][0], outputs['attention_mask'][0]
