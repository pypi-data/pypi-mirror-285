"""
DB executor to run SQL query on user given database
"""

from abc import ABC, abstractmethod
from typing import List, Dict, OrderedDict
import logging

from db_copilot.contract import DatabaseType, SQLDialect, TableSchema, ColumnSchema, TableData, ColumnSecurityLevel
from .sql_utils import DataTypeCategory

_IGNORED_COLUMN_VALUE_STR = "..."
_PROTECTED_COLUMN_VALUE_STR = "******"


class DBExecutor(ABC):
    def __init__(self, tables: List=None) -> None:
        # Defined user selected tables
        self._tables = tables

    @property
    @abstractmethod
    def db_type(self) -> DatabaseType:
        pass
    
    @property
    def sql_dialect(self) -> SQLDialect:
        return SQLDialect.from_db_type(self.db_type)

    @property
    @abstractmethod
    def table_schemas(self) -> OrderedDict[str, TableSchema]:
        pass

    def update_schemas(self, user_settings: Dict[str, dict]):
        """
        Update table schemas with user-defined settings
        """
        for tbl_name, tbl_schema in self.table_schemas.items():
            if tbl_name in user_settings:
                table_setting = user_settings[tbl_name]
                if table_setting.get("description", None):
                    tbl_schema.description = table_setting["description"]

            for col_schema in tbl_schema.columns:
                col_full_name = f"{tbl_name}.{col_schema.name}"
                if col_full_name not in user_settings:
                    continue
                column_setting = user_settings[col_full_name]
                if column_setting.get("description", None):
                    col_schema.description = column_setting["description"]
                if column_setting.get("security_level", None):
                    col_schema.security_level = ColumnSecurityLevel(column_setting["security_level"])

    @abstractmethod
    def get_connection(self):
        pass
        
    @abstractmethod
    def execute_query(self, query: str) -> TableData:
        pass

    def execute_many_queries(self, queries: List[str]) -> List[TableData]:
        assert isinstance(queries, list), "Failed to call `execute_many_queries`, parameter `queries` must be of a list"
        return [self.execute_query(x) for x in queries]
    
    @abstractmethod
    def close(self):
        pass

    def sample_rows(self, sampling_size: int, **kwargs) -> Dict[str, TableData]:
        all_sampling_data = {}
        for tbl_name, tbl_schema in self.table_schemas.items():
            sampling_query = self._get_table_sample_query(tbl_schema, sampling_size)
            if sampling_query is None:
                continue
            sampling_result = self.execute_query(sampling_query)
            all_sampling_data[tbl_name] = sampling_result

            if kwargs.get("verbose", False):
                logging.info("%s Sample %d rows from table %s over.", self.__class__.__name__, sampling_result.num_rows, tbl_name)
        
        return all_sampling_data
    
    def _get_table_sample_query(self, table_schema: TableSchema, sampling_rows: int) -> str:
        def _select_column_values(column: ColumnSchema) -> str:
            if column.security_level > ColumnSecurityLevel.NORMAL:
                return f"'{_PROTECTED_COLUMN_VALUE_STR}' AS {self.sql_dialect.bracket_field_name(column.name)}"

            data_type_category = DataTypeCategory.from_data_type(column.data_type, self.db_type)
            if data_type_category in [DataTypeCategory.Binary, DataTypeCategory.Other]:
                return f"'{_IGNORED_COLUMN_VALUE_STR}' AS {self.sql_dialect.bracket_field_name(column.name)}"
            
            return self.sql_dialect.bracket_field_name(column.name)
        
        if len(table_schema.columns) > 0:
            column_selects = ", ".join([_select_column_values(column) for column in table_schema.columns])

            bracket_table_name = self.sql_dialect.bracket_field_name(table_schema.name)
            if self.sql_dialect in { SQLDialect.TSQL }:
                sampling_query = f"SELECT TOP ({sampling_rows}) {column_selects} FROM {bracket_table_name}"
            elif self.sql_dialect in { SQLDialect.KQL }:
                sampling_query = f"{bracket_table_name} | project {column_selects} | take {sampling_rows}"
            else:
                sampling_query = f"SELECT {column_selects} FROM {bracket_table_name} LIMIT {sampling_rows}"
        else:
            sampling_query = None

        return sampling_query
