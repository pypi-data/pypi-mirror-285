from .baseclass import AzureBlobManager
import os
from azure.storage.blob import BlobServiceClient, ContainerClient

class AzureBlobManagementConnectionString(AzureBlobManager):
    
    def __init__(self, storage_account_name: str) -> None:
        super().__init__(storage_account_name)
        self.name = 'connectionString'

    def _authenticate_(self) -> None:
        self.connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    def _generate_blob_service_client_(self) -> None:
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connect_str)

    def _generate_container_client_(self, container_name: str) -> ContainerClient:
        return ContainerClient.from_connection_string(conn_str=self.connect_str, container_name=container_name)