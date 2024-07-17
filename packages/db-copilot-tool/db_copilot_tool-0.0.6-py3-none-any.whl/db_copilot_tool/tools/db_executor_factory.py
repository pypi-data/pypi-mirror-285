import json
import logging
import os
import struct
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any

import retrying
from azure.identity import (
    ClientSecretCredential,
    ManagedIdentityCredential,
)
from azureml.core import Workspace
from azureml.data.azure_sql_database_datastore import AzureSqlDatabaseDatastore
from azureml.data.azure_storage_datastore import AzureBlobDatastore

# from datastore_utils import CustomDatastore
from db_copilot.db_provider.db_executor import (
    DatabaseType,
    DBExecutor,
    KustoExecutor,
    SheetFileExecutor,
    SQLiteExecutor,
    SQLServerExecutor,
    ClickHouseExecutor,
    CosmosExecutor,
)
from db_copilot_tool.datastore_utils import CustomDatastore
from db_copilot_tool.history_service.history_service import (
    HistoryService,
    history_cache,
)
from db_copilot_tool.telemetry import track_error
from db_copilot_tool.tools.azureml_asset_handler import (
    AzureMlAssetHandler,
    DatastoreDownloader,
)


class CustomDatastoreType(Enum):
    Kusto = "kusto"
    Cosmos = "cosmos"
    ClickHouse = "clickhouse"


@dataclass
class DBExecutorConfig:
    tables: List[str] = None
    column_settings: Dict[str, Dict[str, str]] = None
    metadata: Dict[str, Any] = None


class DBExecutorFactory:
    @staticmethod
    @retrying.retry(stop_max_attempt_number=3, wait_fixed=1000)
    def _get_sqlserver_executor(
        connection_string: str,
        tables: List[str] = None,
        include_views: bool = False,
        attrs_before: Dict[int, Any] = None,
    ) -> DBExecutor:
        return SQLServerExecutor(
            conn_string=connection_string,
            tables=tables,
            include_views=include_views,
            attrs_before=attrs_before,
        )

    @staticmethod
    def create_executor(
        db_type: DatabaseType,
        db_file: str = None,
        connetion_string: str = None,
        extra_config: Dict[str, str] = None,
        tables: List[str] = None,
        column_settings: Dict[str, Dict[str, str]] = None,
    ) -> DBExecutor:
        """Create DBExecutor based on the database type."""
        db_executor: DBExecutor = None
        if db_type == DatabaseType.SQLSERVER:
            if connetion_string is None:
                raise ValueError("connetion_string is required.")
            db_executor = DBExecutorFactory._get_sqlserver_executor(
                connection_string=connetion_string,
                tables=tables,
                include_views=(
                    extra_config.get("include_views", False) if extra_config else False
                ),
                attrs_before=(
                    extra_config.get("attrs_before", None) if extra_config else None
                ),
            )
        elif db_type == DatabaseType.SQLITE:
            if not os.path.exists(db_file):
                raise ValueError(f"db_file:{db_file} does not exist.")
            db_executor = SQLiteExecutor(db_file, tables=tables)
        elif db_type == DatabaseType.KUSTO:
            credential = ClientSecretCredential(
                tenant_id=extra_config["tenant_id"],
                client_id=extra_config["client_id"],
                client_secret=extra_config["client_secret"],
            )
            db_executor = KustoExecutor(
                conn_string=connetion_string,
                database=extra_config["database"],
                database_version=(
                    extra_config["database_version"]
                    if "database_version" in extra_config
                    else None
                ),
                credential=credential,
                tables=tables,
            )
        elif db_type == DatabaseType.SHEET_FILE:
            with open(os.path.join(db_file, "sheets_mapping.json")) as f:
                mapping = json.load(f)
                assert mapping is not None, "sheets_mapping.json is empty"
                assert isinstance(mapping, dict), "sheets_mapping.json is not a dict"
                new_mapping = {}
                for table_name, file_name in mapping.items():
                    assert os.path.exists(
                        os.path.join(db_file, file_name)
                    ), f"{file_name} does not exist"
                    new_mapping[table_name] = os.path.join(db_file, file_name)
            db_executor = SheetFileExecutor(
                json_data=json.dumps(new_mapping), tables=tables
            )
        elif db_type == DatabaseType.CLICKHOUSE:
            db_executor = ClickHouseExecutor(
                host=extra_config["host"],
                user=extra_config["user"] if "user" in extra_config else "default",
                port=extra_config["port"] if "port" in extra_config else "8123",
                password=extra_config["password"] if "password" in extra_config else "",
                tables=tables,
            )
        elif db_type == DatabaseType.COSMOS:
            db_executor = CosmosExecutor(
                url=extra_config["url"],
                key=extra_config["key"],
                container=extra_config["container"],
                db=extra_config["database"],
                tables=tables,
            )
        else:
            raise ValueError("Unsupported database type.")
        if column_settings:
            db_executor.update_schemas(column_settings)
        return db_executor

    @staticmethod
    def create_executor_with_cache(
        asset_uri: str,
        db_executor_config: DBExecutorConfig,
        workspace: Workspace = None,
        history_service: HistoryService = None,
    ):
        """Get the db executor."""
        db_executor_id = f"db_executor_id_{asset_uri}"

        @history_cache(
            db_executor_id,
            history_service=history_service,
            expire_seconds=24 * 60 * 60,
        )
        def get_db_executor_with_cache(asset_uri: str, workspace: Workspace):
            datastore = AzureMlAssetHandler.get_datastore_from_uri(asset_uri, workspace)
            if isinstance(datastore, AzureBlobDatastore):
                with DatastoreDownloader(asset_uri, workspace, True) as download_path:
                    extension = os.path.splitext(download_path)[1]
                    # (db|sdb|sqlite|db3|s3db|sqlite3|sl3|db2|s2db|sqlite2|sl2)
                    if extension and extension.lower() in [
                        ".db",
                        ".sqlite",
                        ".sdb",
                        ".db3",
                        ".s3db",
                        ".sqlite3",
                        ".sl3",
                        ".db2",
                        ".s2db",
                        ".sqlite2",
                        ".sl2",
                    ]:
                        logging.info("Downloaded db file")
                        return (
                            DatabaseType.SQLITE,
                            download_path,
                            None,
                            None,
                            db_executor_config.tables,
                            db_executor_config.column_settings,
                        )
                    elif os.path.exists(
                        os.path.join(download_path, "sheets_mapping.json")
                    ):
                        return (
                            DatabaseType.SHEET_FILE,
                            download_path,
                            None,
                            None,
                            db_executor_config.tables,
                            db_executor_config.column_settings,
                        )
                    else:
                        track_error("Unsupported db file type")
                        raise ValueError("Unsupported db file type")
            elif isinstance(datastore, AzureSqlDatabaseDatastore):
                extra_config = (
                    db_executor_config.metadata if db_executor_config.metadata else {}
                )
                if datastore.client_secret:
                    connection_string = f"Server=tcp:{datastore.server_name}.database.windows.net,1433;Database={datastore.database_name};Uid={datastore.client_id};Pwd={datastore.client_secret};Connection Timeout=300;Authentication=ActiveDirectoryServicePrincipal;"
                elif datastore.password:
                    connection_string = f"Server=tcp:{datastore.server_name}.database.windows.net,1433;Database={datastore.database_name};Uid={datastore.username};Pwd={datastore.password};Connection Timeout=300;"
                elif datastore.service_data_access_auth_identity:
                    connection_string = f"Server=tcp:{datastore.server_name}.database.windows.net,1433;Database={datastore.database_name};Connection Timeout=300;"
                else:
                    raise ValueError(f"Unsupported auth type {datastore.auth_type}")
                return (
                    DatabaseType.SQLSERVER,
                    None,
                    connection_string,
                    extra_config,
                    db_executor_config.tables,
                    db_executor_config.column_settings,
                )
            elif isinstance(datastore, CustomDatastore):
                if (
                    datastore.custom_section.datastore_type.lower()
                    == CustomDatastoreType.Kusto.value.lower()
                ):
                    extra_config = datastore.custom_section.properties.copy()
                    extra_config["client_secret"] = datastore.custom_section.credential
                    return (
                        DatabaseType.KUSTO,
                        None,
                        datastore.custom_section.properties["connection_string"],
                        extra_config,
                        db_executor_config.tables,
                        db_executor_config.column_settings,
                    )
                elif (
                    datastore.custom_section.datastore_type.lower()
                    == CustomDatastoreType.Cosmos.value.lower()
                ):
                    extra_config = datastore.custom_section.properties.copy()
                    return (
                        DatabaseType.COSMOS,
                        None,
                        None,
                        extra_config,
                        db_executor_config.tables,
                        db_executor_config.column_settings,
                    )
                elif (
                    datastore.custom_section.datastore_type.lower()
                    == CustomDatastoreType.ClickHouse.value.lower()
                ):
                    extra_config = datastore.custom_section.properties.copy()
                    return (
                        DatabaseType.CLICKHOUSE,
                        None,
                        None,
                        extra_config,
                        db_executor_config.tables,
                        db_executor_config.column_settings,
                    )
            track_error(f"Unsupported datastore type: {type(datastore)}")
            raise ValueError(f"Unsupported datastore type: {type(datastore)}")

        (
            db_type,
            db_file,
            connection_string,
            extra_config,
            tables,
            column_settings,
        ) = get_db_executor_with_cache(asset_uri, workspace)
        db_executor = DBExecutorFactory.create_executor(
            db_type,
            db_file,
            connection_string,
            extra_config,
            tables,
            column_settings,
        )

        return db_executor
