import pathlib
import tempfile
import unittest
from transformers import AutoTokenizer
from irisml.tasks.create_transformers_raw_tokenizer import Task


class TestCreateTransformersRawTokenizer(unittest.TestCase):
    def test_simple(self):
        outputs = Task(Task.Config('openai/clip-vit-base-patch32')).execute(Task.Inputs())
        self.assertIsNotNone(outputs.tokenizer)

        token = outputs.tokenizer("Answer to the Ultimate Question of Life, The Universe, and Everything")
        self.assertGreater(len(token), 0)
        self.assertIsInstance(token.input_ids, list)
        self.assertIsInstance(token.attention_mask, list)

    def test_load_from_local(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tokenizer = AutoTokenizer.from_pretrained('openai/clip-vit-base-patch32')
            tokenizer.save_pretrained(temp_dir)

            outputs = Task(Task.Config('openai/clip-vit-base-patch32', pathlib.Path(temp_dir))).execute(Task.Inputs())
            self.assertIsNotNone(outputs.tokenizer)
