from enum import Enum
import sqlparse
import logging
from db_copilot.contract import DatabaseType

def is_readonly_query(sql: str) -> bool:
    parsed = sqlparse.parse(sql)
    for parsed_sql in parsed:
        for token in parsed_sql.tokens:
            if token.ttype in (sqlparse.tokens.Keyword, sqlparse.tokens.Keyword.DML, sqlparse.tokens.Keyword.DDL):
                keyword = token.value.upper()
                if keyword in ['UPDATE', 'SET', 'DELETE', 'INSERT', 'CREATE',
                               'ALTER', 'DROP', 'RENAME', 'TRUNCATE', 'REPLACE',
                               'GRANT', 'REVOKE', 'COMMIT', 'ROLLBACK', 'SAVEPOINT',
                               'RESTORE', 'ADD']:
                    return False
    return True


def normalize_column_description(description: str) -> str:
    if not description or not description.strip():
        return None
    
    return description.replace("\n", " ")


class DataTypeCategory(int, Enum):
    Other = 0
    Number = 1
    Text = 2
    Datetime = 3
    Binary = 4

    @classmethod
    def from_data_type(cls, data_type: str, db_type: DatabaseType) -> "DataTypeCategory":
        norm_data_type = cls.normalize_data_type(data_type)

        # Exact-numerics
        if norm_data_type in ["bigint", "numeric", "bit", "smallint", "decimal", "smallmoney", "int", "tinyint", "money"]:
            return DataTypeCategory.Number
        
        # Approximate numerics
        if norm_data_type in ["float", "real"]:
            return DataTypeCategory.Number
        
        # Date and time
        if norm_data_type in ["date", "datetimeoffset", "datetime2", "smalldatetime", "datetime", "time", "timespan", "timestamp"]:
            return DataTypeCategory.Datetime
        
        # Character strings
        if norm_data_type in ["char", "varchar", "text", "string", "dynamic", "guid"]:
            return DataTypeCategory.Text
        
        # Unicode character strings
        if norm_data_type in ["nchar", "nvarchar", "ntext"]:
            return DataTypeCategory.Text
        
        # Binary strings
        if norm_data_type in ["binary", "varbinary", "image"]:
            return DataTypeCategory.Binary
        
        if norm_data_type in ["uniqueidentifier"]:
            return DataTypeCategory.Other

        if norm_data_type in ["cursor", "rowversion", "hierarchyid", "sql_variant", "xml", "table", "geometry", "geography"]:
            return DataTypeCategory.Other
        
        # Datatypes In SQLite
        if norm_data_type in ["integer", "real", "bool", "number"]:
            return DataTypeCategory.Number
        
        if norm_data_type in ["text", "varchar2"]:
            return DataTypeCategory.Text
        
        if norm_data_type in ["blob"]:
            return DataTypeCategory.Other

        # Datatypes In Kusto
        if norm_data_type in ["bool", "boolean", "int", "long", "real", "double", "decimal"]:
            return DataTypeCategory.Number

        logging.warning("Column data type `%s`/`%s` is not supported now.", db_type, data_type)
        return DataTypeCategory.Other

    @classmethod
    def normalize_data_type(cls, data_type: str):
        to_be_returned_index = 0
        splitted_data_type = data_type.lower().split('(')

        # If the length is bigger than 1, then other attributes like Nullable might exist
        # Existing known cases are 
        # 1. Nullable from clickhouse
        if (len(splitted_data_type) > 1):
            other_attributes = splitted_data_type[0]
            if other_attributes in ["nullable"]:
                to_be_returned_index = 1
        
        return splitted_data_type[to_be_returned_index].strip()
