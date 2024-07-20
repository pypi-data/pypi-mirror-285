import pathlib
import tempfile
import unittest

import torch
import transformers
from irisml.tasks.create_transformers_tokenizer import Task


class TestCreateTransformersTokenizer(unittest.TestCase):
    def test_simple(self):
        outputs = Task(Task.Config('openai/clip-vit-base-patch32')).execute(Task.Inputs())
        self.assertIsNotNone(outputs.tokenizer)

        token = outputs.tokenizer("Answer to the Ultimate Question of Life, The Universe, and Everything")
        self.assertIsInstance(token, tuple)
        self.assertEqual(len(token), 2)

        input_ids, attention_mask = token
        self.assertIsInstance(input_ids, torch.Tensor)
        self.assertIsInstance(attention_mask, torch.Tensor)
        self.assertEqual(input_ids.shape, attention_mask.shape)

    def test_load_local_filepath(self):
        tokenizer = transformers.AutoTokenizer.from_pretrained('openai/clip-vit-base-patch32')
        with tempfile.TemporaryDirectory() as temp_dir:
            tokenizer.save_pretrained(temp_dir)

            outputs = Task(Task.Config(local_filepath=pathlib.Path(temp_dir))).execute(Task.Inputs())
            self.assertIsNotNone(outputs.tokenizer)

            original_tokens = tokenizer("Answer to the Ultimate Question of Life, The Universe, and Everything", return_tensors='pt', padding='max_length', max_length=77)
            new_tokens = outputs.tokenizer("Answer to the Ultimate Question of Life, The Universe, and Everything")

            self.assertIsInstance(new_tokens, tuple)
            self.assertTrue(torch.equal(new_tokens[0], original_tokens['input_ids'][0]))
            self.assertTrue(torch.equal(new_tokens[1], original_tokens['attention_mask'][0]))
