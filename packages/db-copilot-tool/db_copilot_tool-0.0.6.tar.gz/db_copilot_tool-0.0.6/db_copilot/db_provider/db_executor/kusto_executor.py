import json
import logging
import re
import threading
from datetime import datetime
from functools import cached_property
import time
from typing import OrderedDict

from tqdm import tqdm

from db_copilot.contract import (
    ColumnSchema,
    TableSchema,
    DatabaseType,
    TableData,
    SQLDialect,
)
from db_copilot.db_provider.db_executor.db_executor import DBExecutor

logger = logging.getLogger("kusto_executor")

# Seconds to try re-connect to database
_RECONNECT_SECONDS = 5 * 60


def dependable_import():
    try:
        import azure.identity
        import azure.kusto.data
        import azure.kusto.data.exceptions
    except ImportError as e:
        raise ValueError(
            f"Could not import required python package ({e.msg}). Please install dbcopilot with `pip install dbcopilot[extensions] ...` "
        )
    return azure.identity, azure.kusto.data, azure.kusto.data.exceptions


class KustoExecutor(DBExecutor):
    def __init__(
        self, conn_string: str, database: str, database_version: str, **kwargs
    ) -> None:
        super().__init__(kwargs.get("tables", None))
        assert conn_string is not None
        assert database is not None
        self._conn_string = conn_string
        self._database = database
        self._database_version = database_version
        (
            self._azure_identity,
            self._azure_kusto_data,
            self._azure_kusto_data_exceptions,
        ) = dependable_import()
        self.credential = kwargs.get("credential", None)
        self._lock = threading.Lock()
        self._kql_dialect = SQLDialect.from_db_type(DatabaseType.KUSTO)
        self._connect_to_server()

    @property
    def db_type(self) -> str:
        return DatabaseType.KUSTO

    def _normalize_field_name(self, name: str) -> str:
        regex = r"\[\'(.+)\'\]"
        matches = re.findall(regex, name)
        return matches[0] if len(matches) > 0 else name

    @cached_property
    def table_schemas(self) -> OrderedDict[str, TableSchema]:
        if self._database_version == "security":
            tables = self.get_table_schemas_security_database()
        else:
            tables = self.get_table_schemas()

        functions = self.get_function_schemas()

        schemas = OrderedDict({**tables, **functions})
        return schemas

    def get_table_schemas(self):
        table_details = self._client.execute_mgmt(
            self._database, ".show tables details | project TableName, TotalRowCount"
        ).primary_results[0]
        tables = OrderedDict()

        for t in table_details.rows:
            table_name = self._normalize_field_name(t["TableName"])
            if self._tables is not None and table_name not in self._tables:
                continue

            table_schema = self._client.execute_mgmt(
                self._database,
                f".show table {self._kql_dialect.bracket_field_name(table_name)} cslschema | project Schema",
            ).primary_results[0]
            assert table_schema.rows_count == 1

            table_schema = table_schema.rows[0]["Schema"]
            column_schemas = []
            for column in table_schema.split(","):
                column_name, column_type = column.split(":")
                column_schemas.append(
                    ColumnSchema(self._normalize_field_name(column_name), column_type)
                )

            # try to get samples to make sure the table is accessible
            try:
                eqr = self.execute_query(
                    "{} | project {} | take 5".format(
                        self._kql_dialect.bracket_field_name(t["TableName"]),
                        ", ".join(
                            [
                                self._kql_dialect.bracket_field_name(col.name)
                                for col in column_schemas
                            ]
                        ),
                    )
                )
            except Exception as e:
                logging.warning(
                    "Failed to get samples for table `{}`: {}".format(t["TableName"], e)
                )
                continue

            tables[t["TableName"]] = TableSchema(
                name=t["TableName"],
                columns=column_schemas,
                num_rows=t["TotalRowCount"],
                primary_key=[],
                foreign_keys=[],
            )
        return tables

    def get_table_schemas_security_database(self):
        table_details = json.loads(
            self._client.execute_mgmt(
                self._database, ".show schema as json"
            ).primary_results[0][0]["DatabaseSchema"]
        )["Databases"][self._database]["Tables"]
        tables = OrderedDict()

        for table, schema in tqdm(table_details.items(), desc="Getting table schemas"):
            table_name = self._normalize_field_name(table)
            if self._tables is not None and table_name not in self._tables:
                continue

            column_schemas = []
            for column in schema["OrderedColumns"]:
                column_name = self._normalize_field_name(column["Name"])
                column_type = column["CslType"]
                column_schemas.append(ColumnSchema(column_name, column_type))
            # try to get samples to make sure the table is accessible
            try:
                total_row_count = self.execute_query(
                    "{} | count".format(
                        self._kql_dialect.bracket_field_name(table_name)
                    )
                )["Count"][0]
            except:
                logging.warning(
                    "Failed to get total row count for table `{}`".format(table_name)
                )
                continue

            tables[table_name] = TableSchema(
                name=table_name,
                columns=column_schemas,
                num_rows=total_row_count,
                primary_key=[],
                foreign_keys=[],
            )
        return tables

    def get_function_schemas(self):
        functions = OrderedDict()

        function_details = (
            self._client.execute_mgmt(self._database, ".show functions")
            .primary_results[0]
            .rows
        )
        for function in tqdm(function_details, desc="Getting function schemas"):
            function_name = self._normalize_field_name(function["Name"])
            if self._tables is not None and function_name not in self._tables:
                continue
            try:
                one_row = self.execute_query(
                    "{} | take 1".format(
                        self._kql_dialect.bracket_field_name(function_name)
                    )
                )
                column_schemas = [
                    ColumnSchema(column_name, column_type)
                    for column_name, column_type in zip(
                        one_row.columns, one_row.column_types
                    )
                ]
                total_row_count = len(
                    one_row.data
                )  # self.execute_query("{} | count".format(self._kql_dialect.bracket_field_name(function_name)))["Count"][0]
            except:
                logging.warning(
                    "Failed to get total row count for function `{}`".format(
                        function_name
                    )
                )
                continue

            functions[function_name] = TableSchema(
                name=function_name,
                columns=column_schemas,
                num_rows=total_row_count,
                primary_key=[],
                foreign_keys=[],
                description=function["DocString"],
            )
        return functions

    def get_connection(self):
        with self._lock:
            if (
                datetime.now() - self._last_conn_time
            ).total_seconds() > _RECONNECT_SECONDS:
                self._connect_to_server()
            return self._client

    def _create_kusto_client(self, kcsb):
        return self._azure_kusto_data.KustoClient(kcsb)

    def _connect_to_server(self):
        try:
            self._client.close()
        except:
            pass

        if self.credential:
            credential = self.credential
        else:
            credential = self._azure_identity.ChainedTokenCredential(
                self._azure_identity.ManagedIdentityCredential(),
                self._azure_identity.AzureCliCredential(),
            )
        kcsb = self._azure_kusto_data.KustoConnectionStringBuilder.with_azure_token_credential(
            self._conn_string, credential
        )
        self._client = self._create_kusto_client(kcsb)
        self._last_conn_time = datetime.now()

    def close(self):
        self._client.close()

    INNER_ERROR_REGEX = r"\(inner error: (.*)\)"

    def execute_query(self, query: str, **kwargs) -> TableData:
        # todo: check if the query is read only. we need a kusto language parser.
        logging.info("Kusto Executor run query: `%s`", query)
        retry_count = 3
        while True:
            try:
                if query.strip().startswith("."):
                    dataset = self._client.execute_mgmt(self._database, query)
                else:
                    dataset = self._client.execute_query(self._database, query)
                break
            except self._azure_kusto_data_exceptions.KustoApiError as e:
                logging.warning(
                    "Failed to execute query: `%s`, error: `%s`",
                    query,
                    e.get_api_error(),
                )
                try:
                    error_message = json.loads(
                        json.loads(
                            re.findall(
                                self.INNER_ERROR_REGEX, e.error.message, re.MULTILINE
                            )[0]
                        )["message"]
                    )["error"]["innererror"]["innererror"]["message"]
                    simplified_error = Exception(error_message)
                except:
                    simplified_error = e
                raise simplified_error
            except Exception as e:
                logging.warning("Failed to execute query: `%s`, error: `%s`", query, e)
                retry_count -= 1
                if retry_count <= 0:
                    raise e
                time.sleep(1)
                self._connect_to_server()

        # todo: need to check the other primary results.
        table = dataset.primary_results[0]
        col_names = [c.column_name for c in table.columns]
        col_types = [c.column_type for c in table.columns]
        data = [row.to_list() for row in table]
        return TableData(columns=col_names, column_types=col_types, data=data)
