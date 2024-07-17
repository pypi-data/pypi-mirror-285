"""
ClickHouse Database Executor
"""
from typing import OrderedDict, List
from functools import cached_property
import logging
import threading
from datetime import datetime
import re

from db_copilot.contract import ColumnSchema
from .db_executor import DatabaseType, TableSchema, DBExecutor, TableData

logger = logging.getLogger("clickhouse_executor")

# Seconds to try re-connect to database
_RECONNECT_SECONDS = 60


def dependable_import():
    try:
        import clickhouse_connect
    except ImportError as e:
        raise ValueError(
            f"Could not import required python package ({e.msg}). Please install dbcopilot with `pip install dbcopilot[extensions] ...` "
        )
    return clickhouse_connect


class ClickHouseExecutor(DBExecutor):
    def __init__(self, host: str, user: str, **kwargs) -> None:
        super().__init__(tables=kwargs.get("tables", None))
        self.clickhouse_connect = dependable_import()
        assert None not in [host, user]
        self._conn_args = {
            "host": host,
            "user": user,
            **{key: kwargs[key] for key in ["port", "password"] if key in kwargs},
        }

        self._lock = threading.Lock()
        self._connect_to_server()

    @property
    def db_type(self) -> DatabaseType:
        return DatabaseType.CLICKHOUSE

    @cached_property
    def table_schemas(self) -> OrderedDict[str, TableSchema]:
        assert (
            self._tables is not None
        ), "tables is required for ClickHouse to fetch db schema"
        return {
            table_name: self.get_table_schema(table_name) for table_name in self._tables
        }

    def get_connection(self):
        """
        60 seconds timeout is set same with default session_timeout
        session_timeout: Number of seconds of inactivity before the identified by the session id will timeout and no longer be considered valid. Defaults to 60 seconds.
        """
        with self._lock:
            if (
                datetime.now() - self._last_conn_time
            ).total_seconds() > _RECONNECT_SECONDS:
                self._connect_to_server()
            return self._conn

    def _connect_to_server(self):
        self._conn = self.clickhouse_connect.get_client(**self._conn_args)
        self._last_conn_time = datetime.now()

    def close(self):
        self._conn.close()

    def _convert_type(self, data_type: str):
        if "String" in data_type:
            return "text"
        if "Float" in data_type:
            return "float"
        if "Int" in data_type:
            return "int"
        return data_type

    def get_table_schema(self, table_name: str) -> TableSchema:
        sql_query = "DESCRIBE TABLE {}".format(table_name)
        table_info = self.execute_query(sql_query)

        column_schemas: List[ColumnSchema] = []
        data = list(table_info.rows(as_dict=True))
        primary_columns = []
        for row in data:
            column_schema = ColumnSchema(
                name=row["name"],
                data_type=self._convert_type(row["type"]),
            )
            column_schemas.append(column_schema)

        row_cnt_df = self.execute_query(f"SELECT COUNT(1) FROM {table_name}")
        row_cnt = list(row_cnt_df.rows(as_dict=False))[0][0]

        # TODO: get primary_key and foreign_keys from tables
        return TableSchema(
            name=table_name,
            columns=column_schemas,
            primary_key=primary_columns,
            num_rows=row_cnt,
            foreign_keys=[],
        )

    def execute_query(self, query: str) -> TableData:
        # logging.info("ClickHouse Executor run query: `%s`", query)
        result = self.get_connection().query(query)

        col_names = list(result.column_names)
        col_types = [
            self._get_column_data_type(type(col_type).__name__)
            for col_type in result.column_types
        ]

        # convert result_rows to list
        data = [list(row) for row in result.result_rows]

        return TableData(columns=col_names, column_types=col_types, data=data)

    @staticmethod
    def _get_column_data_type(data_type_class: str):
        data_type = data_type_class.lower()
        data_type = re.sub(r"\d+$", "", data_type)

        return {"uint": "int", "string": "str"}.get(data_type, data_type)
