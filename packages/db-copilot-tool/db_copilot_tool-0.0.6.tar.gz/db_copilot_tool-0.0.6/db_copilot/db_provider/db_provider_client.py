"""
DB Provider Agent implementation by AzureML endpoint.
It is a client to post requests to call remote DBProviderService.
"""
import logging
from typing import Dict
from db_copilot.contract import DBProviderAgent, DBProviderAgentFactory, DatabaseType, DBSnapshot, CodeBlock, SQLExecuteResult

from .azureml_endpoint import AzureMLEndpoint

class DBProviderClient(DBProviderAgent):
    def __init__(self, db_id: str, db_type: DatabaseType, api: AzureMLEndpoint, session_id: str=None) -> None:
        self._db_id = db_id
        self._db_type = db_type if not isinstance(db_type, str) else DatabaseType(db_type)
        self.api = api
        self.session_id = session_id

    @property
    def db_type(self) -> DatabaseType:
        return self._db_type

    def retrieve_schema(self, utterance: str = None) -> DBSnapshot:
        request = {
            'query_type': 'schema_retrieval',
            'db_id': self._db_id,
            'question': utterance
        }

        schema_dict = self.api(json=request, azureml_sessionid=self.session_id)
        return DBSnapshot.from_dict(schema_dict)

    def execute_code(self, code: CodeBlock) -> SQLExecuteResult:
        request = {
            "query_type": "code_execution",
            'db_id': self._db_id,
            'code': code.to_dict()
        }

        result_dict = self.api(json=request)
        return SQLExecuteResult.from_dict(result_dict)


    @classmethod
    def from_config(cls, **kwargs) -> DBProviderAgent:
        return cls(
            kwargs.get("db_id"),
            kwargs.get("db_type"),
            kwargs.get("api", None)
        )


class DBProviderClientFactory(DBProviderAgentFactory):
    def __init__(self, default_api: AzureMLEndpoint) -> None:
        super().__init__()
        self.default_api = default_api
        self.add_db_providers_from_api(api=default_api)
    
    def create_db_provider(self, db_id: str, **kwargs) -> DBProviderAgent:
        api = kwargs.get("api", None)

        query = {
            "query_type": "create_new",
            "db_id": db_id,
            **kwargs
        }

        if api:
            api = AzureMLEndpoint.from_string(api)
        else:
            api = self.default_api
        
        result, session_id = api(json=query, return_azureml_sessionid=True)
        db_type = DatabaseType(result["db_type"])
        db_provider = DBProviderClient(db_id=db_id, db_type=db_type, api=api, session_id=session_id)
        self._db_providers[db_id] = db_provider
        logging.info("Create DB provider `{}`/{} over with {} tables.".format(db_id, db_type, result["tables"]))
        return db_provider

    @classmethod
    def from_api(cls, api_string: str) -> "DBProviderClientFactory":
        api = AzureMLEndpoint.from_string(api_string)
        return cls(api)

    def add_db_providers_from_api(self, api: AzureMLEndpoint=None, db_id_maps: Dict[str, str]=None) -> int:
        # TODO: remove expired db providers
        if isinstance(api, str):
            api = AzureMLEndpoint.from_string(api)
        else:
            assert isinstance(api, AzureMLEndpoint), "Parameter `api` must be api connect string or instance of AzureMLEndpoint"

        prev_db_providers = len(self._db_providers)
        dbs = api(json={'query_type': 'ping'})
        for db_id, db_type in dbs:
            if db_id_maps and db_id not in db_id_maps:
                continue
            
            self._db_providers[db_id_maps[db_id] if db_id_maps else db_id] = DBProviderClient(db_id, DatabaseType(db_type), api=api)
        
        logging.info("Add {} db providers from API `{}` over!!!".format(len(self._db_providers) - prev_db_providers, api.api_url))
        return len(dbs)
    
    def get_db_provider(self, db_id: str, load_from_azure_blob_path: str=None) -> DBProviderAgent:
        if db_id in self._db_providers:
            return self._db_providers[db_id]
        else:
            if load_from_azure_blob_path is None:
                raise KeyError(f"DB provider `{db_id}` not found, and no azure blob path provided.")
            return self.create_db_provider(db_id=db_id, load_from_azure_blob_path=load_from_azure_blob_path)