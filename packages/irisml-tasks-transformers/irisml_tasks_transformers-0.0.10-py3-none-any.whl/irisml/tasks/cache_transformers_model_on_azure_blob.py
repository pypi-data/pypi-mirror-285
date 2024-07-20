import dataclasses
import logging
import pathlib
import tempfile
from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient
import transformers
import irisml.core

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Cache a model from transformers on Azure Blob Storage.

    This task will download a model from transformers and upload it to Azure Blob Storage.
    If the model already exists in the blob storage, it will skip the upload.

    Config:
        name (str): The name of the model to download from transformers.
        container_url (str): The URL of the Azure Blob Storage container to upload the model to.
        blob_path_prefix (str): The prefix to use for the blob path. The model will be uploaded to {container_url}/{blob_path_prefix}/{name}.
    """
    VERSION = '0.1.1'
    CACHE_ENABLED = False

    @dataclasses.dataclass
    class Config:
        name: str
        container_url: str
        blob_path_prefix: str = ''
        overwrite: bool = False

    def execute(self, inputs):
        blob_prefix = f'{self.config.blob_path_prefix}/{self.config.name}' if self.config.blob_path_prefix else self.config.name
        container_client = ContainerClient.from_container_url(self.config.container_url, credential=DefaultAzureCredential())
        existing_blob_names = list(container_client.list_blob_names(name_starts_with=blob_prefix + '/'))
        if existing_blob_names and not self.config.overwrite:
            logger.info(f"Found existing blobs: {existing_blob_names}. Skipping upload.")
        else:
            logger.debug(f"Downloading a model from transformers: {self.config.name}")
            model = transformers.AutoModel.from_pretrained(self.config.name)
            processor = transformers.AutoProcessor.from_pretrained(self.config.name)
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir = pathlib.Path(temp_dir)
                model.save_pretrained(temp_dir)
                processor.save_pretrained(temp_dir)
                for filepath in temp_dir.iterdir():
                    blob_path = f'{blob_prefix}/{filepath.name}'
                    logger.info(f"Uploading {filepath} to {blob_path}")
                    container_client.upload_blob(blob_path, filepath.read_bytes(), max_concurrency=8, timeout=300, overwrite=self.config.overwrite)

            logger.info(f"Uploaded model to {self.config.container_url}/{blob_prefix}.")

        return self.Outputs()
