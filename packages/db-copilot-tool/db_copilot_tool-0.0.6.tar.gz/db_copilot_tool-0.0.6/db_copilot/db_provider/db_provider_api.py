"""
DB provider azureml endpoint scoring entry
"""
import os
import json
import yaml
from enum import Enum
from typing import Dict
from datetime import datetime
from dataclasses import dataclass
import logging
import traceback
from pathlib import Path
from pympler import asizeof

import sys
sys.path.append(Path(__file__).parent.parent.parent.as_posix())

from db_copilot.db_provider import DBProviderAgentFactory, DBProviderServiceFactory, DBProviderService, CodeBlock
from db_copilot.telemetry import enable_appinsights_logging
_PKG_ABS_PATH = Path(__file__).parent.parent.as_posix()

_DEFAULT_DB_PROVIDER_CAPACITY = 1_000

class DBProviderAPIStatusCode(int, Enum):
    # TODO: support more
    Succeeded = 0
    Invalid_input = 1
    Internal_exception = 2


@dataclass
class DBProviderAPIResult:
    status_code: DBProviderAPIStatusCode = DBProviderAPIStatusCode.Succeeded
    elapsed_ms: int = -1
    data: Dict = None
    error_msg: str = None

    def to_dict(self) -> Dict:
        resp = { 'status_code': self.status_code.value, 'elapsed_ms': self.elapsed_ms }
        if self.error_msg:
            resp["error_msg"] = self.error_msg
        
        if self.data is not None:
            if hasattr(self.data, "to_dict"):
                resp["data"] = self.data.to_dict()
            else:
                resp["data"] = self.data
        
        return resp

def init(**kwargs) -> DBProviderAgentFactory:
    # Enable appinsights logging if connection string is set
    if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
        # Activity infos will be saved into `customEvents` table in AppInsights
        enable_appinsights_logging()

    global _factory
    capacity = int(os.getenv("DB_PROVIDER_CAPACITY", f"{_DEFAULT_DB_PROVIDER_CAPACITY}"))
    logging.info("DB provider capacity: {}".format(capacity))

    if os.getenv("DB_CONFIG_JSON", None):
        configs = json.loads(os.getenv("DB_CONFIG_JSON"))
        _factory = DBProviderServiceFactory.from_configs(configs, capacity=capacity, **kwargs)
    elif os.getenv("DB_CONFIG_PATH", None):
        config_path: str = os.path.join(_PKG_ABS_PATH, os.getenv("DB_CONFIG_PATH"))
        assert os.path.exists(config_path), f"Config file not found `{config_path}`"
        with open(config_path, 'r', encoding='utf-8') as fr:
            if config_path.endswith(".yml") or config_path.endswith(".yaml"):
                configs = yaml.safe_load(fr)
            else:
                configs = json.load(fr)
        if isinstance(configs, dict):
            configs = [configs]
        _factory = DBProviderServiceFactory.from_configs(configs, capacity=capacity, **kwargs)
    else:
        raise ValueError("DB_CONFIG_JSON or DB_CONFIG_PATH is required to init API")
    
    logging.info("Create database provider over!!!")
    return _factory

def run_db_provider(query: dict, **kwargs):
    if 'query_type' not in query:
        return DBProviderAPIResult(
            status_code=DBProviderAPIStatusCode.Invalid_input,
            error_msg="`query_type` is required for all types of queries.",
            elapsed_ms=0
        ).to_dict()

    query_type = query.pop('query_type')
    logging.info(" >>> Run {} ...".format(query_type))
    start = datetime.now()
    result = DBProviderAPIResult()

    try:
        if query_type == "ping":
            result.data = [(db_id, provider.db_type.value) for db_id, provider in _factory._db_providers.items()]
            result.elapsed_ms = int((datetime.now() - start).total_seconds() * 1000)
            return result.to_dict()

        if query_type == "mem_usage":
            # return db_id, mem_usage (in MB), table_snapshots (list of table schema dict)
            result.data = [(db_id, asizeof.asizeof(provider)/(1024 * 1024), [t.schema.to_dict() for t in provider.retrieve_schema().table_snapshots]) \
                           for db_id, provider in _factory._db_providers.items()]
            result.elapsed_ms = int((datetime.now() - start).total_seconds() * 1000)            
            return result.to_dict()

        if query_type == "clear_cache":
            max_duration = query.get("max_duration", 3600 * 24)
            result.data = _factory.clear_cache(max_duration=max_duration)
            result.elapsed_ms = int((datetime.now() - start).total_seconds() * 1000)
            return result.to_dict()

        if 'db_id' not in query:
            return DBProviderAPIResult(
                status_code=DBProviderAPIStatusCode.Invalid_input,
                error_msg="`db_id` is required to run `{}`".format(query_type),
                elapsed_ms=0
            ).to_dict()
    
        db_id = query.pop('db_id')
        if query_type == 'create_new':
            db_provider = _factory.create_db_provider(db_id=db_id, **{**query, **kwargs} )
            result.data = { 'tables': len(db_provider.db_executor.table_schemas), 'db_type': db_provider.db_type }
            result.elapsed_ms = int((datetime.now() - start).total_seconds() * 1000)
            logging.info(" >>> Run {} over, cost = {}ms.".format(query_type, result.elapsed_ms))
            return result.to_dict()
        db_provider: DBProviderService = _factory.get_db_provider(db_id)
        if query_type == "schema_retrieval":
            result.data = db_provider.retrieve_schema(utterance=query.get("question", None))
        elif query_type == "code_execution":
            result.data = db_provider.execute_code(CodeBlock.from_dict(query["code"]))
        else:
            raise NotImplementedError("Query type `{}` is not implemented".format(query_type))

        result.elapsed_ms = int((datetime.now() - start).total_seconds() * 1000)
        logging.info(" >>> Run {} over, cost = {}ms.".format(query_type, result.elapsed_ms))
        return result.to_dict()

    except Exception as ex:
        logging.info(" >>> Run {} failed, error = {}.".format(query_type, traceback.format_exc()))
        return DBProviderAPIResult(
            status_code=DBProviderAPIStatusCode.Internal_exception,
            error_msg=str(ex),
            elapsed_ms=int((datetime.now() - start).total_seconds() * 1000),
        ).to_dict()


def run(data):
    query = json.loads(data)
    return run_db_provider(query)
