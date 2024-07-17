"""
Definition for DB Provider Agent
"""

import abc
from .db_core import DatabaseType, SQLDialect, DBSnapshot
from .tool_core import CodeBlock, CodeExecuteResult
from .utils.lru import LRUCacheDict

class DBProviderAgent(abc.ABC):
    """
    Agent provides APIs wrapped on a database:
        1) retrieve query-relevant data
        2) execute generated code
    """
    @property
    @abc.abstractmethod
    def db_type(self) -> DatabaseType:
        """
        Database type
        """

    @property
    def sql_dialect(self) -> SQLDialect:
        """
        SQL dialect of the given database
        """
        return SQLDialect.from_db_type(self.db_type)

    @classmethod
    @abc.abstractmethod
    def from_config(cls, **kwargs) -> "DBProviderAgent":
        """
        Create a DB provider agent instance from config
        """

    @abc.abstractmethod
    def retrieve_schema(self, utterance: str=None, **kwargs) -> DBSnapshot:
        """
        Retrieve relevant database snapshot when given a question utterance on the database
        """

    @abc.abstractmethod
    def execute_code(self, code: CodeBlock) -> CodeExecuteResult:
        """
        Execute generated code and return execution result on the database
        """

class DBProviderAgentFactory:
    def __init__(self, capacity: int=1000) -> None:
        self._db_providers = LRUCacheDict(capacity=capacity, del_callback=lambda db_id, db_provider: db_provider.close())

    def get_db_provider(self, db_id: str) -> DBProviderAgent:
        if db_id not in self._db_providers:
            raise KeyError(f"DB provider `{db_id}` not found.")
        return self._db_providers[db_id]
    
    def add_db_provider(self, db_id: str, db_provider: DBProviderAgent, overwrite: bool=True):
        if db_id in self._db_providers and not overwrite:
            raise KeyError(f"Failed to add DB provider `{db_id}` as it exists in factory.")
        prev_db_provider = self._db_providers.get(db_id, None)
        if prev_db_provider is not None:
            prev_db_provider.close()
        self._db_providers[db_id] = db_provider

    @abc.abstractmethod
    def create_db_provider(self, db_id: str, **kwargs) -> DBProviderAgent:
        raise NotImplementedError()
