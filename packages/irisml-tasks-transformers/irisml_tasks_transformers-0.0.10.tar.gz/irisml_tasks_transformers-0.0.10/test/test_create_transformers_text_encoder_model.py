import unittest
import unittest.mock
import torch
from irisml.tasks.create_transformers_text_encoder_model import Task


class TestCreateTransformersTextEncoderModel(unittest.TestCase):
    def test_simple(self):
        with unittest.mock.patch('socket.socket') as m:
            m.side_effect = RuntimeError
            model = Task(Task.Config('openai/clip-vit-base-patch32')).execute(Task.Inputs()).model

        self.assertIsInstance(model, torch.nn.Module)
        outputs = model.prediction_step((torch.zeros((1, 10), dtype=torch.long), torch.ones((1, 10), dtype=torch.long)))
        self.assertIsInstance(outputs, torch.Tensor)
        self.assertEqual(outputs.dtype, torch.float32)
        self.assertEqual(outputs.shape, (1, 512))
