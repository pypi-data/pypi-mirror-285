import importlib
import os
import json
import requests
from typing import Dict, List
import re
import logging
from functools import lru_cache
import uuid
import time

from db_copilot.contract import DatabaseType, DBSnapshot, DBProviderAgent, DBProviderAgentFactory, CodeBlock, SQLExecuteResult
from db_copilot.db_provider.db_executor import DBExecutor, SQLiteExecutor, SQLServerExecutor, ClickHouseExecutor, SheetFileExecutor, KustoExecutor, CosmosExecutor
from db_copilot.db_provider.grounding import ORTEmbeddingModel, GroundingService
from db_copilot.db_provider.utils import StopWatcher
from db_copilot.telemetry import get_logger, track_activity
from .db_provider_config import DBProviderConfig
from azure.storage.blob import BlobClient

logger = get_logger("db_copilot.db_provider")
Embedding_Molel_Key = 'embedding_model'

def parse_conn_string(conn_string: str) -> Dict[str, str]:
    try:
        conn_items = conn_string.split(";")
        server = conn_items[0].split("//")[1] if '//' in conn_items[0] else conn_items[0]
        conn_args = { s.split('=')[0]: s.split('=')[1] for s in conn_items[1:] if s }
        return { 'server': server, **conn_args}
    except:
        raise ValueError("Invalid connect string: ``{}``, sample format: ``<your_server>;database=<your_database>;user=<your_user>;password=<your_password>;``".format(conn_string))

def short_uuid_string() -> str:
    uuid_string = str(uuid.uuid4()).replace('-', '')
    return uuid_string[:8]

def fetch_data_from_url_or_path(url: str):
    if os.path.exists(url):
        with open(url, 'rb') as fr:
            return fr.read()
    try:
        data = requests.get(url).content
        return data
    except Exception as ex: # pylint: disable=broad-exception-caught
        raise ValueError(f"Failed to fetch data from `{url}`: {ex}")


def save_bytes(data: bytes, saved_path: str):
    os.makedirs(os.path.dirname(saved_path), exist_ok=True)
    with open(saved_path, 'wb') as fw:
        fw.write(data)


class DBProviderService(DBProviderAgent):
    def __init__(self, db_executor: DBExecutor, grounding_service: GroundingService) -> None:
        self.db_executor = db_executor
        self.grounding_service = grounding_service

    @property
    def db_id(self) -> str:
        return self.grounding_service.service_id
    
    @property
    def db_type(self) -> DatabaseType:
        return self.db_executor.db_type
    
    def close(self):
        self.db_executor.close()
        logging.warning("DB Provider `{}`/{} is destroyed.".format(self.db_id, self.db_type))

    @classmethod
    def from_config(cls, config: DBProviderConfig, **kwargs) -> "DBProviderService":
        """
        Create DB Provider service from user-defined config
        """
        with track_activity(logger, "create db provider") as activity_logger:
            sw = StopWatcher()
            if isinstance(config, dict):
                config = DBProviderConfig.from_dict(config)
            else:
                assert isinstance(config, DBProviderConfig), "A `DBProviderConfig` instance or dict object is required"

            # Connect to database and update user settings
            db_executor: DBExecutor = cls._create_db_executor(config)
            if config.column_settings:
                db_executor.update_schemas(user_settings=config.column_settings)

            cost1 = sw.elapsed_ms()
            embedding_model = kwargs.pop(Embedding_Molel_Key, None) or config.metadata.get(Embedding_Molel_Key, None) or ORTEmbeddingModel.default_distilroberta()
            cost2 = sw.elapsed_ms() - cost1
            grounding_service = GroundingService.build_from_db_executor(
                db_id=config.db_id,
                db_executor=db_executor,
                embedding_model=embedding_model,
                config=config.grounding_config,
                knowledge_pieces=config.knowledge_pieces,
                **{**config.metadata, **kwargs}
            )
            cost3 = sw.elapsed_ms() - cost2 - cost1
            db_provider = DBProviderService(db_executor=db_executor, grounding_service=grounding_service)
            logger.info("Create DB provider `%s` over, type = %s, cost = %d(%d+%d+%d)ms.", config.db_id, db_executor.db_type, sw.elapsed_ms(), cost1, cost2, cost3)
            return db_provider
    
    @lru_cache(maxsize=1024)
    def retrieve_schema(self, utterance: str = None, **kwargs) -> DBSnapshot:
        with track_activity(logger, "retrieve_schema") as activity_logger:
            logger.info("Retrieve schema for utterance on DB `%s`: %s", self.db_id, utterance)
            if utterance is None:
                return self.grounding_service.default_db_snapshot
            return self.grounding_service.search(utterance, **kwargs)
    
    def execute_code(self, code: CodeBlock) -> SQLExecuteResult:
        with track_activity(logger, "execute_code") as activity_logger:
            try:
                sw = StopWatcher()
                logger.info("Execute query on DB `%s`: %s", self.db_id, code.source)
                result = self.db_executor.execute_query(code.source)
                return SQLExecuteResult(
                    cost_ms=sw.elapsed_ms(),
                    data=result
                )
            except Exception as ex:
                logging.error("Execute query `%s` error: %s", code.source, str(ex))
                return SQLExecuteResult(
                    cost_ms=sw.elapsed_ms(),
                    exception_message=str(ex)
                )

    @staticmethod
    def _create_db_executor(config: DBProviderConfig) -> DBExecutor:
        with track_activity(logger, "create_db_executor") as activity_logger:
            if 'db_executor_class' in config.metadata:
                db_executor_class_fullname = config.metadata.get('db_executor_class')
                module_name, class_name = db_executor_class_fullname.rsplit(".", 1)
                module = importlib.import_module(module_name)
                class_ = getattr(module, class_name)
                instance = class_(tables=config.selected_tables, conn_string=config.conn_string, **config.metadata)
                return instance

            raw_conn_string = config.get_value(config.conn_string)
            conn_str_match = re.match(r'^(\w+)://(.*)$', raw_conn_string)
            assert conn_str_match is not None, "Invalid conn string format"
            db_type, conn_string = DatabaseType(conn_str_match.group(1)), conn_str_match.group(2)
            conn_string = config.get_value(conn_string)

            activity_logger.activity_info["db_type"] = db_type
            logger.info("Start to create %s DB executor for `%s` ...", db_type, config.db_id)

            db_executor: DBExecutor = None
            if db_type == DatabaseType.SQLITE:
                db_bytes = None
                if isinstance(conn_string, str):
                    db_bytes = fetch_data_from_url_or_path(conn_string)
                elif isinstance(conn_string, (bytes, list)):
                    db_bytes = bytes(conn_string)
                else:
                    raise ValueError("A local path or remote url or file bytes required to connect to SQLite.")
                db_path = f"data/sqlite_dbs/{config.db_id}_{short_uuid_string()}.sqlite"
                save_bytes(db_bytes, db_path)
                db_executor = SQLiteExecutor(db_path, is_local=False, tables=config.selected_tables)
            elif db_type == DatabaseType.SQLSERVER:
                db_executor = SQLServerExecutor(conn_string, tables=config.selected_tables, include_views=config.metadata.get('include_views', False))
            elif db_type == DatabaseType.SHEET_FILE:
                db_path = f"data/sqlite_dbs/{config.db_id}_{short_uuid_string()}.sheet.sqlite"
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                db_executor = SheetFileExecutor(json_data=conn_string, db_path=db_path, tables=config.selected_tables)
            elif db_type == DatabaseType.CLICKHOUSE:
                conn_args = parse_conn_string(conn_string)
                conn_args["host"] = conn_args.pop("server")
                db_executor = ClickHouseExecutor(**conn_args, tables=config.selected_tables)
            elif db_type == DatabaseType.KUSTO:
                database = config.metadata.get("database", None)
                database_version = config.metadata.get("database_version", None)
                db_executor = KustoExecutor(conn_string, database, database_version, tables=config.selected_tables)
            elif db_type == DatabaseType.COSMOS:
                #CONN_STRING = "cosmos://URL;DB_NAME;CONTAINER_NAME;PRIMARY_KEY"
                items = conn_string.split(';')
                kwargs = {
                    'url': items[0], 
                    'key': items[3], 
                    'db': items[1],
                    'container': items[2],
                    'tables': config.selected_tables
                }
                db_executor = CosmosExecutor(**kwargs)
            else:
                raise NotImplementedError(f"Database type `{db_type}` is not supported yet.")

            return db_executor

class DBProviderServiceFactory(DBProviderAgentFactory):
    @classmethod
    def from_configs(cls, configs: List, capacity: int=1000, **kwargs) -> "DBProviderServiceFactory":
        factory = cls(capacity)
        sw = StopWatcher()
        for config in configs:
            db_provider = DBProviderService.from_config(config, **kwargs)
            factory.add_db_provider(db_provider.db_id, db_provider)
        
        logging.info("Create %d DB providers over, cost = %dms.", len(factory._db_providers), sw.elapsed_ms())
        return factory

    def create_db_provider(self, db_id: str, **kwargs) -> DBProviderAgent:
        logging.info("Try to create DB provider `{}` with args {} ...".format(db_id, kwargs.keys()))
        load_from_azure_blob_path = kwargs.pop("load_from_azure_blob_path", None)
        save_to_azure_blob_path = kwargs.pop("save_to_azure_blob_path", None)
        if load_from_azure_blob_path:
            blob_data = BlobClient.from_connection_string(**load_from_azure_blob_path).download_blob()
            content = blob_data.readall()
            kwargs = json.loads(content)
        db_provider = DBProviderService.from_config({ "db_id": db_id, **kwargs}, **kwargs)
        self.add_db_provider(db_id=db_id, db_provider=db_provider)
        if save_to_azure_blob_path:
            blob_client = BlobClient.from_connection_string(**save_to_azure_blob_path)
            blob_client.upload_blob(json.dumps(kwargs))

        return db_provider

    def clear_cache(self, max_duration: int):
        cleared_db_paths = []
        has_local_file = lambda db_provider: hasattr(db_provider.db_executor, "database") and isinstance(db_provider.db_executor.database, str) and os.path.isfile(db_provider.db_executor.database)

        def clear_callback(db_id, db_provider):
            if has_local_file(db_provider):
                cleared_db_paths.append((db_id, db_provider.db_executor.database))
            else:
                cleared_db_paths.append((db_id, None))
        self._db_providers.clear_cache(max_duration, callback=clear_callback)

        db_inuse = set([db_provider.db_executor.database for db_provider in self._db_providers.values() if has_local_file(db_provider)])
        for file_path in os.listdir("data/sqlite_dbs"):
            full_path = f"data/sqlite_dbs/{file_path}"
            mtime = os.path.getmtime(full_path)
            if mtime < time.time() - max_duration and full_path not in db_inuse:
                os.remove(full_path)
                cleared_db_paths.append((None, full_path))
        return cleared_db_paths