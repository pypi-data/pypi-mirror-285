import logging
import os
import re
import shutil
import tempfile

from azure.ai.ml import MLClient
from azure.identity import ManagedIdentityCredential
from azureml.core import Datastore, Workspace
from azureml.core.authentication import (
    ArmTokenAuthentication,
    InteractiveLoginAuthentication,
)
from azureml.data.azure_storage_datastore import AzureBlobDatastore
from db_copilot_tool.datastore_utils import CustomDatastore
from db_copilot_tool.telemetry import get_logger, track_activity, track_info


class AzureMlAssetHandler:
    """This class is to handle the Azure ML assets, such as datastore, data connection, etc."""

    subscription_identifier = "subscription_id"
    resource_group_identifier = "resource_group"
    workspace_identifier = "workspace"
    asset_type_identifier = "asset_type"
    asset_name_identifier = "asset_name"
    rest_identifier = "rest"

    @staticmethod
    def parse_datastore_uri(datastore_uri: str, workspace: Workspace = None):
        """Parse the datastore uri to get the subscription, resource group, workspace, datastore, and path"""

        parsed_uri = AzureMlAssetHandler.parse_asset_uri(datastore_uri)
        if parsed_uri:
            assert parsed_uri[AzureMlAssetHandler.asset_type_identifier] == "datastores"
            path: str = None
            path_regex = r"^paths\/(?P<path>.+)$"
            path_match = re.match(
                path_regex, parsed_uri[AzureMlAssetHandler.rest_identifier]
            )
            if path_match:
                path = path_match.group("path")
            subscription = parsed_uri[AzureMlAssetHandler.subscription_identifier]
            resource_group = parsed_uri[AzureMlAssetHandler.resource_group_identifier]
            workspace = parsed_uri[AzureMlAssetHandler.workspace_identifier]
            datastore = parsed_uri[AzureMlAssetHandler.asset_name_identifier]
            return subscription, resource_group, workspace, datastore, path
        elif workspace:
            regex = r"azureml://datastores/(?P<datastore_name>[^/]+)\/?(?P<rest>.*)?$"
            match = re.match(regex, datastore_uri)
            if match:
                full_uri = f"azureml://subscriptions/{workspace.subscription_id}/resourcegroups/{workspace.resource_group}/workspaces/{workspace.name}/datastores/{match.group('datastore_name')}"
                if match.group("rest"):
                    full_uri += f"/{match.group('rest')}"
                return AzureMlAssetHandler.parse_datastore_uri(full_uri)
            else:
                raise ValueError(f"Invalid datastore uri: {datastore_uri}")
        else:
            raise ValueError(f"Invalid datastore uri: {datastore_uri}")

    @staticmethod
    def parse_asset_uri(asset_uri: str):
        """Get the asset type from the asset uri"""
        uri_regex = r"^azureml:\/\/subscriptions\/(?P<subscription_id>[^\/]*)\/resourcegroups\/(?P<resource_group>[^\/]*)\/workspaces\/(?P<workspace>[^\/]*)\/(?P<asset_type>[^\/]*)\/(?P<asset_name>[^\/]*)\/?(?P<rest>.*)?$"
        match = re.match(uri_regex, asset_uri)
        if match:
            return match.groupdict()
        return None

    @staticmethod
    def get_azure_auth():
        """Retrieve an access token via REST."""
        client_id = os.environ.get("UAI_CLIENT_ID")
        credential = ManagedIdentityCredential(client_id=client_id)
        track_info("Retrieved token successfully.")
        return credential

    @staticmethod
    def get_auth():
        """Get the authentication for the workspace"""
        if os.environ.get("MSI_ENDPOINT"):
            track_info("Getting MSI authentication")
            token = AzureMlAssetHandler.get_azure_auth().get_token(
                "https://management.core.windows.net/"
            )
            return ArmTokenAuthentication(token.token)
        else:
            track_info("Getting interactive authentication")
            # raise NotImplementedError()
            return InteractiveLoginAuthentication()

    @staticmethod
    def get_datastore_from_uri(
        datastore_uri: str, workspace: Workspace = None
    ) -> Datastore:
        """Get the datastore from the datastore uri"""
        (
            subscription,
            resource_group,
            workspace_name,
            datastore_name,
            _,
        ) = AzureMlAssetHandler.parse_datastore_uri(datastore_uri, workspace)
        if workspace is None:
            # TODO: use MLClient to get the workspace
            workspace = Workspace(
                subscription_id=subscription,
                resource_group=resource_group,
                workspace_name=workspace_name,
                auth=AzureMlAssetHandler.get_auth(),
            )
        else:
            assert workspace.subscription_id == subscription
            assert workspace.resource_group == resource_group
            assert workspace.name == workspace_name
        datastore = Datastore.get(workspace, datastore_name)
        if datastore.datastore_type.lower() == "custom":
            datastore = CustomDatastore.get(workspace, datastore_name)
        return datastore


class DatastoreDownloader:
    DATA_STORE_CACHE_FOLDER = "/tmp/datastore_cache"

    def __init__(
        self, url: str, workspace: Workspace = None, with_cache: bool = False
    ) -> None:
        datastore = AzureMlAssetHandler.get_datastore_from_uri(url, workspace=workspace)
        if isinstance(datastore, AzureBlobDatastore):
            _, _, _, _, relative_path = AzureMlAssetHandler.parse_datastore_uri(url)
            if not relative_path:
                raise ValueError(
                    f"Invalid datastore uri: {url}. Must specify relative path"
                )
            self.datastore: AzureBlobDatastore = datastore
            self.relative_path = relative_path
            self.with_cache = with_cache
        else:
            raise ValueError(f"Invalid datastore: {datastore}")

    def __enter__(self):
        logger = get_logger("datastore_downloader")
        with track_activity(logger, "download") as activity_logger:
            self.temp_dir = tempfile.mkdtemp()
            file_count = self.datastore.download(
                self.temp_dir, prefix=self.relative_path, overwrite=True
            )
            activity_logger.activity_info["file_count"] = file_count
            logging.info(
                f"Downloaded {file_count} files from {self.datastore.name}/{self.relative_path} to {self.temp_dir}"
            )
            download_path = os.path.join(self.temp_dir, self.relative_path)
            if self.with_cache:
                activity_logger.activity_info["with_cache"] = True
                target_path = os.path.join(
                    DatastoreDownloader.DATA_STORE_CACHE_FOLDER,
                    self.datastore.name,
                    self.relative_path,
                )
                if not os.path.exists(os.path.dirname(target_path)):
                    logging.info(f"Creating directory {os.path.dirname(target_path)}")
                    os.makedirs(os.path.dirname(target_path))
                if os.path.isfile(download_path):
                    shutil.copyfile(download_path, target_path)
                else:
                    shutil.copytree(download_path, target_path, dirs_exist_ok=True)
                logging.info(f"Copied {download_path} to {target_path}")
                return target_path
            return os.path.join(self.temp_dir, self.relative_path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


class DatastoreUploader:
    def __init__(self, url: str, src_path: str, workspace: Workspace = None) -> None:
        datastore = AzureMlAssetHandler.get_datastore_from_uri(url, workspace=workspace)
        if isinstance(datastore, AzureBlobDatastore):
            _, _, _, _, relative_path = AzureMlAssetHandler.parse_datastore_uri(url)
            if not relative_path:
                raise ValueError(
                    f"Invalid datastore uri: {url}. Must specify relative path"
                )
            self.datastore: AzureBlobDatastore = datastore
            self.relative_path = relative_path
        else:
            raise ValueError(f"Invalid datastore: {datastore}")
        self.src_path = src_path

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger = get_logger("datastore_uploader")
        with track_activity(logger, "upload") as activity_logger:
            for dirpath, dirnames, filenames in os.walk(self.src_path):
                # logging.info(dirpath)
                for dirname in dirnames:
                    logging.info(os.path.join(dirpath, dirname))
            if exc_val is None:
                self.datastore.upload(
                    src_dir=self.src_path,
                    target_path=self.relative_path,
                    overwrite=True,
                    show_progress=True,
                )
            else:
                logging.error(f"Error uploading files: {exc_val}")
