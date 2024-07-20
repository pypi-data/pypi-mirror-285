import pickle
import unittest
import torch
from irisml.tasks.create_transformers_model import Task


class TestCreateTransformersModel(unittest.TestCase):
    def test_clip(self):
        outputs = Task(Task.Config('openai/clip-vit-base-patch32')).execute(Task.Inputs())
        self.assertIsInstance(outputs.model, torch.nn.Module)

        loss = outputs.model.training_step((torch.zeros(1, 3, 224, 224), torch.zeros(1, 8, dtype=torch.int)), torch.zeros((1, ), dtype=torch.long))
        self.assertIsInstance(loss['loss'], torch.Tensor)

        # Use new tokenizer format
        loss = outputs.model.training_step((torch.zeros(1, 3, 224, 224), (torch.zeros(1, 8, dtype=torch.int), torch.zeros(1, 8, dtype=torch.int))), torch.zeros((1, ), dtype=torch.long))
        self.assertIsInstance(loss['loss'], torch.Tensor)

        # Test that the model can be serialized and deserialized
        deserialized_model = pickle.loads(pickle.dumps(outputs.model))
        test_inputs = torch.rand((1, 3, 224, 224))
        outputs1 = outputs.model.image_model(test_inputs)
        outputs2 = deserialized_model.image_model(test_inputs)
        self.assertTrue(torch.allclose(outputs1, outputs2))
