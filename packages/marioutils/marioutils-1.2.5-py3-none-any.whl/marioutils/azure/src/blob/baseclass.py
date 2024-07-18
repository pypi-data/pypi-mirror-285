from abc import ABC, abstractmethod
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import pathlib
from typing import BinaryIO


class AzureBlobManager(ABC):

    def __init__(self, storage_account_name: str) -> None:
        self.account_url = f"https://{storage_account_name}.blob.core.windows.net"
        self.storage_account_name = storage_account_name
        self._authenticate_()
        self.blob_service_client: BlobServiceClient = None
        self.name: str = ''

    def __del__(self):
        if self.blob_service_client:
            self.blob_service_client.close()

    @abstractmethod
    def _authenticate_(self) -> None:
        pass

    @abstractmethod
    def _generate_blob_service_client_(self) -> None:
        """Generates a class property client for interacting with the whole blob service
        """
        pass

    @abstractmethod
    def _generate_container_client_(self, container_name: str) -> ContainerClient:
        """Generates a client for interacting with a specific container

        Args:
            container_name (str): The name of the container to interact with

        Returns:
            ContainerClient
        """
        pass

    def _generate_blob_client_(self, container_name: str, blob: str) -> BlobClient:
        """Generates and returns a client for interacting with a specific blob resource

        Args:
            container_name (str): The container where the resource lives

        Returns:
            BlobClient: The client to interact with the resource
        """
        if not self.blob_service_client:
            self._generate_blob_service_client_()

        return self.blob_service_client.get_blob_client(
            container=container_name,
            blob=blob
            )

    def upload_blob_from_file(
            self,
            file_path: str,
            container_name: str,
            **kwargs
            ) -> dict:
        """Uploads a system file as a blob file to a given container

        Args:
            file_path (str): The path where the file lives
            container_name (str): The container where the file will live

            :Keyword Arguments:
            **virtual_folder (str, optional): The name of the virtual folder where the blob will be uploaded
        """

        # file logic
        file = pathlib.Path(file_path)
        if not file.is_file():
            raise ValueError('The provided path was not found')

        # kwargs logic
        if 'virtual_folder' in kwargs:
            virtual_folder = kwargs.get('virtual_folder')
            if not virtual_folder:
                raise RuntimeError('Could not obtain the virutal folder name')
            blob_path = f'{virtual_folder}/{file.name}'

        blob_client = self._generate_blob_client_(container_name=container_name, blob=blob_path)

        # reading file
        with open(file_path, 'rb') as data:
            res = blob_client.upload_blob(data)

        return res

    def upload_blob_stream(
            self, 
            container_name: str,
            blob_name: str,
            data: BinaryIO,
            **kwargs) -> dict:
        """Uploads a binary file from an api service as a blob file to a given container\
        (TESTED ONLY ON FASTAPI)

        Args:
            container_name (str): The container where the blob will be uploaded to
            blob_name (str): The name of the blob file to be uploaded with
            data (BinaryIO): The binary data

            :Keyword Arguments:
            **virtual_folder (str, optional): The name of the virtual folder where the blob will be uploaded

        Returns:
            dict: _description_
        """

        # kwargs logic
        if 'virtual_folder' in kwargs:
            virtual_folder = kwargs.get('virtual_folder')
            if not virtual_folder:
                raise RuntimeError('Could not obtain the virutal folder name')
            blob_path = f'{virtual_folder}/{blob_name}'

        blob_client = self._generate_blob_client_(
            container_name=container_name,
            blob=blob_path)
        blob_client.upload_blob(data)

    def get_container_blob_names(self, container_name: str) -> list:
        """Retrives the names of the blob files in a given container

        Args:
            container_name (str): The container in which to look for

        Returns:
            list[str]: List of the blob names
        """
        container_client = self._generate_container_client_(
            container_name=container_name)
        blob_list = container_client.list_blob_names()
        return list(blob_list)

    def download_blob(self, container: str, blob_name: str) -> bytes:
        """Downloads bytes for a given blob resource

        Args:
            container (str): The container where the blob resource lives
            blob_name (str): The name of the blob resource, it should include the virtual folder if exists

        Returns:
            bytes: The content of the file
        """
        container_client = self._generate_container_client_(container_name=container)
        
        content: bytes = container_client.download_blob(blob=blob_name).readall()

        return content