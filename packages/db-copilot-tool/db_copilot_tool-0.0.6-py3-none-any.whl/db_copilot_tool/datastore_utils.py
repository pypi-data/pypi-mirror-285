"""File for CustomDatastore the Class."""

from azureml.data.datastore_client import _DatastoreClient
from azureml.core import Datastore, Workspace
from azureml._restclient.models import DataStore as DataStoreDto
from msrest.serialization import Model


class CustomDatastoreProperties(Model):
    """CustomDatastoreProperties Class."""

    _attribute_map = {
        "datastore_type": {"key": "datastoreType", "type": "str"},
        "credential": {"key": "credential", "type": "str"},
        "properties": {"key": "properties", "type": "{str}"},
    }

    def __init__(
        self, datastore_type: str, credential: str = None, properties: dict = None
    ):
        """Initialize the class."""
        super(CustomDatastoreProperties, self).__init__()
        self.datastore_type = datastore_type
        self.credential = credential
        self.properties = properties or {}


class CustomDatastore(DataStoreDto):
    """CustomDatastore Class."""

    _attribute_map = {
        "name": {"key": "name", "type": "str"},
        "data_store_type": {"key": "dataStoreType", "type": "str"},
        "has_been_validated": {"key": "hasBeenValidated", "type": "bool"},
        "tags": {"key": "tags", "type": "{str}"},
        "custom_section": {"key": "customSection", "type": "CustomDatastoreProperties"},
    }

    def __init__(
        self,
        name: str,
        data_store_type: str,
        credential=None,
        properties=None,
        has_been_validated=None,
        tags=None,
    ):
        """Initialize the class."""
        super().__init__(
            name,
            "Custom",
            has_been_validated,
            tags,
            azure_storage_section=None,
            azure_data_lake_section=None,
            azure_sql_database_section=None,
            azure_postgre_sql_section=None,
            azure_my_sql_section=None,
            hdfs_section=None,
            gluster_fs_section=None,
        )
        self.custom_section = CustomDatastoreProperties(
            datastore_type=data_store_type, credential=credential, properties=properties
        )

    @staticmethod
    def _dto_to_datastore(dto):
        custom_section = dto.additional_properties.get("customSection")
        return CustomDatastore(
            dto.name,
            custom_section["datastoreType"],
            custom_section["credential"],
            custom_section["properties"],
            dto.has_been_validated,
            dto.tags,
        )

    @staticmethod
    def get(workspace: Workspace, name: str):
        """get."""
        dto = _DatastoreClient._get_client(workspace, None, None).data_stores.get(
            workspace._subscription_id,
            workspace._resource_group,
            workspace._workspace_name,
            name,
            _DatastoreClient._custom_headers,
        )
        return CustomDatastore._dto_to_datastore(dto)

    def create_or_update(self, workspace: Workspace):
        """create_or_update."""
        return (
            Datastore._client()._register(
                workspace,
                dto=self,
                create_if_not_exists=True,
                skip_validation=True,
                overwrite=True,
                auth=None,
                host=None,
            ),
        )
