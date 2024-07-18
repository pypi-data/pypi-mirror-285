
from .baseclass import AzureBlobManager
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContainerClient


class AzureBlobManagementDefaultCredential(AzureBlobManager):
    
    def __init__(self, storage_account_name: str) -> None:
        super().__init__(storage_account_name)
        self.name = 'defaultCredential'


    def _authenticate_(self) -> None:
        self.default_credential = DefaultAzureCredential()

    def _generate_blob_service_client_(self) -> None:
        self.blob_service_client = BlobServiceClient(
            account_url= self.account_url,
            credential= self.default_credential
        )

    def _generate_container_client_(self, container_name: str) -> ContainerClient:
        return ContainerClient(
            account_url= self.account_url,
            credential= self.default_credential,
            container_name=container_name
        )
