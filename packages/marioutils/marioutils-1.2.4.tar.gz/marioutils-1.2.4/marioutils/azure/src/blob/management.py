

from .defautCredential import AzureBlobManagementDefaultCredential
from .connString import AzureBlobManagementConnectionString
from .baseclass import AzureBlobManager


def create_blob_manager(manager: str, storage_account_name: str) -> AzureBlobManager:
    managers = {
        'defaultCredential': AzureBlobManagementDefaultCredential(storage_account_name),
        'connectionString': AzureBlobManagementConnectionString(storage_account_name)
    }
    if manager not in managers:
        raise ValueError(f"No factory is implemented for provided value {manager}")
    return managers[manager]
