from ..src import create_blob_manager
from ..src.blob.connString import AzureBlobManagementConnectionString
from ..src.blob.defautCredential import AzureBlobManagementDefaultCredential
from ..src.blob.baseclass import AzureBlobManager
import pytest


@pytest.mark.parametrize(
    "test_name,_class",
    [
        ('defaultCredential', AzureBlobManagementDefaultCredential),
        ('connectionString', AzureBlobManagementConnectionString)
    ])
def test_correct_manager(test_name, _class):

    manager: AzureBlobManager = create_blob_manager(test_name, storage_account_name='servoerpblobtest')

    assert isinstance(manager, _class)


@pytest.mark.parametrize(
    "test_name,_class",
    [
        ('defaultCredential', AzureBlobManagementDefaultCredential)
    ])
def test_connection(test_name, _class):

    manager: AzureBlobManager = create_blob_manager(test_name, storage_account_name='servoerpblobtest')
    manager._generate_blob_service_client_()
    assert manager.blob_service_client.api_version != ''