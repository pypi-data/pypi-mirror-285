from typing import OrderedDict
from functools import cached_property

from db_copilot.contract import TableSchema, DatabaseType, TableData
from db_copilot.db_provider.db_executor import DBExecutor


class MockExecutor(DBExecutor):
    """
    @Description: A mock executor that contains one sample table and will always return None for each code execution request.
    @Author: Zeqi Lin (alias: zelin)
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(kwargs.get("tables", None))
        self.description = kwargs.get('description', None)

    @property
    def db_type(self) -> str:
        return DatabaseType.OTHER
    
    @cached_property
    def table_schemas(self) -> OrderedDict[str, TableSchema]:
        return {
            "[SampleTableName]": TableSchema(name="[SampleTableName]", columns=[], num_rows=-1, primary_key=[], foreign_keys=[])
        }

    def get_connection(self):
        pass
    
    def close(self):
        pass
    
    def execute_query(self, query: str, **kwargs) -> TableData:
        return None
