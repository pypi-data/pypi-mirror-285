import unittest
import torch
from irisml.tasks.create_transformers_text_model import TextGenerationModel


class TestCreateTransformersTextModel(unittest.TestCase):
    def test_text_generation_model(self):
        mock_model = unittest.mock.MagicMock()
        mock_preprocessor = unittest.mock.MagicMock()

        model = TextGenerationModel(mock_model, mock_preprocessor)
        inputs = [('test text', [torch.rand(3, 32, 32)])]
        outputs = model(inputs)
        self.assertIsInstance(outputs, list)

        mock_model.generate.assert_called_once()
