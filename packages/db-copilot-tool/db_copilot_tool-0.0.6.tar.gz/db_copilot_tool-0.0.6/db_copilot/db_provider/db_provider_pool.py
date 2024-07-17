"""
A pool implementation to host multiple db provider agents.
"""
import logging

from typing import List
from db_copilot.contract import DBProviderAgentFactory
from .db_provider_client import DBProviderClientFactory

class DBProviderPool:
    def __init__(self, endpoints: List[DBProviderAgentFactory]) -> None:
        assert endpoints and len(endpoints) > 0, 'Invalid empty or null db provider endpoint'
        self._endpoints = endpoints
    
    def __len__(self) -> int:
        return len(self._endpoints)

    def get_db_provider_agent(self, user_id: str) -> DBProviderAgentFactory:
        assert user_id, "Invalid empty or null user id"
        idx = user_id.__hash__() % len(self._endpoints)
        logging.info("Map user `{}` to db provider endpoint {}/{}.".format(user_id, idx, len(self._endpoints)))
        return self._endpoints[idx]

    @classmethod
    def from_apis(cls, api_strings: List[str]) -> "DBProviderPool":
        endpoint_apis = api_strings.split(';;')
        db_provider_endpoints = [DBProviderClientFactory.from_api(api) for api in endpoint_apis]
        logging.info("Init DB provider pool from {} apis.".format(len(endpoint_apis)))
        return cls(db_provider_endpoints)
