import dataclasses
import logging
import pathlib
import typing
import torch
from transformers import AutoTokenizer
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Create a Tokenizer using transformers library. Return the tokenizer as-is.

    Config:
        name (str): Name of the tokenizer to load from transformers library.
        filepath (Path): If provided, load the tokenizer from the given filepath instead of the huggingface server.
    """
    VERSION = '0.1.1'

    @dataclasses.dataclass
    class Config:
        name: str
        filepath: typing.Optional[pathlib.Path] = None

    @dataclasses.dataclass
    class Outputs:
        tokenizer: typing.Callable

    def execute(self, inputs):
        if self.config.filepath:
            logger.info(f"Loading a tokenizer from {self.config.filepath}")
            tokenizer = AutoTokenizer.from_pretrained(self.config.filepath)
        else:
            tokenizer = AutoTokenizer.from_pretrained(self.config.name)
        return self.Outputs(tokenizer)

    def dry_run(self, inputs):
        return self.Outputs(fake_tokenizer)


def fake_tokenizer(*args, **kwargs):
    return torch.zeros(1, 77, dtype=torch.long)
