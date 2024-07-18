from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions


class StorageType(Enum):
    """Enum class for storage types."""

    AZURE = "azureBlobStroage"
    AWS = "s3"
    GCP = "googleCloudStorage"
    LOCAL = "local"


class StorageConfig:
    """Base storage configuration class."""

    def __init__(self, storage_type: StorageType):
        """
        Initializes the StorageConfig.

        Args:
            storage_type (StorageType): The type of storage service.
        """
        self.storage_type = storage_type
        self.credentials: Optional[dict] = None

    def generate_image_properties(self) -> list:
        """
        Generates file properties like signed url, size, ... for the storage service.
        [{"url": "https://example.com/image.jpg", "size": 1024}]
        """
        properties = []
        return properties


class AzureStorageConfig(StorageConfig):
    """Azure storage configuration class."""

    def __init__(self, account_name: str, container_name: str, account_key: str):
        """
        Initializes the AzureStorageConfig.

        Args:
            account_name (str): The Azure storage account name.
            container_name (str): The Azure storage container name.
            account_key (str): The Azure storage account key.
        """
        super().__init__(StorageType.AZURE)
        self.account_name = account_name
        self.container_name = container_name
        self.account_key = account_key

    def generate_image_properties(self) -> list:
        """
        Azure 블랍 스토리지에 저장된 이미지 파일의 URL과 크기를 반환합니다.
        """
        properties = []
        blob_service_client = BlobServiceClient(
            account_url=f"https://{self.account_name}.blob.core.windows.net", credential=self.account_key
        )
        container_client = blob_service_client.get_container_client(self.container_name)

        # List all blobs in the container
        blob_list = container_client.list_blobs()

        # Iterate through the blobs and generate SAS URLs
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]

        for blob in blob_list:
            if any(blob.name.lower().endswith(ext) for ext in image_extensions):
                sas_token = generate_blob_sas(
                    account_name=self.account_name,
                    container_name=self.container_name,
                    blob_name=blob.name,
                    account_key=self.account_key,
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.utcnow() + timedelta(hours=24 * 30),  # Set the expiry time as needed
                )
                sas_url = (
                    f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob.name}?{sas_token}"
                )
                blob_client = container_client.get_blob_client(blob)
                blob_properties = blob_client.get_blob_properties()
                properties.append({"url": sas_url, "size": blob_properties.size})

        return properties
