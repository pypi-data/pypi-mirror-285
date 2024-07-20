import unittest
import unittest.mock
from irisml.tasks.cache_transformers_model_on_azure_blob import Task


def _fake_save_pretrained(dir_path):
    (dir_path / 'a.pth').touch()
    (dir_path / 'b.pth').touch()


class TestCacheTransformersModelOnAzureBlob(unittest.TestCase):
    def test_overwrite(self):
        with unittest.mock.patch('irisml.tasks.cache_transformers_model_on_azure_blob.ContainerClient') as mock_container_client, \
             unittest.mock.patch('transformers.AutoModel') as mock_auto_model, unittest.mock.patch('transformers.AutoProcessor'):
            mock_auto_model.from_pretrained.return_value.save_pretrained = _fake_save_pretrained
            mock_container_client.from_container_url.return_value.list_blob_names.return_value = ['a.pth', 'b.pth']

            Task(Task.Config(name='model_name', container_url='https://example.com/container/', overwrite=True)).execute(Task.Inputs())

            mock_container_client.from_container_url.return_value.list_blob_names.assert_called_once()
            self.assertEqual(mock_container_client.from_container_url.return_value.upload_blob.call_count, 2)
