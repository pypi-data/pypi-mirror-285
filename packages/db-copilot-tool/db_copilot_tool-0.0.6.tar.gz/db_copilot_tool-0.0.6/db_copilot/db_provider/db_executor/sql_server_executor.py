"""
SQLServer Database Executor
"""
import os
from typing import OrderedDict
import threading
from functools import cached_property
from datetime import datetime, timedelta, timezone
import struct
import logging
import pyodbc
from azure.identity import ManagedIdentityCredential

from db_copilot.contract import ColumnSchema, TableSchema, DatabaseType, TableData
from db_copilot.db_provider.db_executor import DBExecutor
from .sql_utils import is_readonly_query

logger = logging.getLogger("sqlserver_executor")

# Seconds to try re-connect to database
_RECONNECT_SECONDS = 5 * 60


class SQLServerExecutor(DBExecutor):
    def __init__(self, conn_string: str, **kwargs) -> None:
        super().__init__(kwargs.get("tables", None))
        assert conn_string is not None
        self._conn_string = conn_string
        self.include_views = kwargs.get('include_views', False)
        self.attrs_before = None
        self._lock = threading.Lock()
        self._connect_to_server()

    @property
    def db_type(self) -> str:
        return DatabaseType.SQLSERVER

    @cached_property
    def table_schemas(self) -> OrderedDict[str, TableSchema]:
        all_table_schema_query = """SELECT
	'[' + s.name + '].[' + t.name + ']' AS table_name,
    c.name AS column_name,
	dt.name AS data_type,
	c.column_id AS ORDINAL_POSITION
FROM sys.columns c
INNER JOIN sys.tables t on t.object_id = c.object_id
INNER JOIN sys.types dt on dt.system_type_id = c.system_type_id and dt.is_user_defined = 0 and dt.name !='sysname' and dt.is_assembly_type=0
INNER JOIN sys.schemas s ON s.schema_id = t.schema_id --and s.Name = TABLE_SCHEMA
UNION
	SELECT
        '[' + s.name + '].[' + t.name + ']' AS table_name,
		c.name AS column_name,
		'_PK_',
		-2
	FROM 
		sys.indexes i
		JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
		JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
		JOIN sys.objects o ON c.object_id = o.object_id
		JOIN sys.tables t on t.object_id = c.object_id
		JOIN sys.schemas s on s.schema_id = t.schema_id
	WHERE
		i.is_primary_key = 1 and o.type='u'
UNION
	SELECT
		'[' + SCHEMA_NAME(tab1.schema_id) + '].[' + tab1.name + ']' AS table_name,
		col1.name AS [column],
		'[' + SCHEMA_NAME(tab2.schema_id) + '].[' +  tab2.name + ']\t' + col2.name AS [referenced_column],
		-1
	FROM sys.foreign_key_columns fkc
	INNER JOIN sys.objects obj
		ON obj.object_id = fkc.constraint_object_id
	INNER JOIN sys.tables tab1
		ON tab1.object_id = fkc.parent_object_id
	INNER JOIN sys.columns col1
		ON col1.column_id = parent_column_id AND col1.object_id = tab1.object_id
	INNER JOIN sys.tables tab2
		ON tab2.object_id = fkc.referenced_object_id
	INNER JOIN sys.columns col2
		ON col2.column_id = referenced_column_id AND col2.object_id = tab2.object_id
"""

        if self.include_views:
            all_table_schema_query += """
UNION
    SELECT
        '[' + v.TABLE_SCHEMA + '].[' + v.TABLE_NAME + ']' AS table_name,
        c.COLUMN_NAME AS column_name,
        c.DATA_TYPE AS data_type,
        0 AS ORDINAL_POSITION
    FROM INFORMATION_SCHEMA.VIEWS v  
    INNER JOIN INFORMATION_SCHEMA.COLUMNS c ON v.TABLE_SCHEMA = c.TABLE_SCHEMA AND v.TABLE_NAME = c.TABLE_NAME
"""

        all_table_schema_query += "order by ORDINAL_POSITION"

        table_schemas: OrderedDict[str, TableSchema] = {}
        all_table_schema_result = self.execute_query(all_table_schema_query)

        ignored_tables = set()
        for row in all_table_schema_result.rows(as_dict=False):
            table_name, column_name, data_type, position = row

            # Ignore user not-selected tables
            # TODO: support more in user selected tables
            if self._tables and table_name not in self._tables:
                ignored_tables.add(table_name)
                continue
            
            if table_name not in table_schemas:
                table_schemas[table_name] = TableSchema(name=table_name, columns=[], num_rows=-1, primary_key=[], foreign_keys=[])

            # PK
            if position == -2:
                table_schemas[table_name].primary_key.append(column_name)
            elif position == -1:
                if table_name not in table_schemas:
                    continue
                ref_table, ref_column = data_type.split("\t")
                table_schemas[table_name].foreign_keys.append((column_name, ref_table, ref_column))
            else:
                column_schema = ColumnSchema(column_name, data_type)
                table_schemas[table_name].columns.append(column_schema)

        logging.info("There are %d tables are selected, %d tables are ignored.", len(table_schemas), len(ignored_tables))

        try:
            query_all_row_count = """SELECT
      '[' + SCHEMA_NAME(sOBJ.schema_id) + '].[' + sOBJ.name + ']' AS [TableName],
      SUM(sPTN.Rows) AS [RowCount]
FROM
      sys.objects AS sOBJ
      INNER JOIN sys.partitions AS sPTN
            ON sOBJ.object_id = sPTN.object_id
WHERE
      sOBJ.type = 'U'
      AND sOBJ.is_ms_shipped = 0x0
      AND index_id < 2 -- 0:Heap, 1:Clustered
GROUP BY 
      sOBJ.schema_id, sOBJ.name
ORDER BY [TableName]
    """
            all_row_cnt_results = self.execute_query(query_all_row_count)
            for result in all_row_cnt_results.rows(as_dict=True):
                if result['TableName'] not in table_schemas:
                    continue
                table_schemas[result['TableName']].num_rows = result['RowCount']
            return table_schemas
        except:
            all_row_cnt_queries = [
                "select count(1) AS row_cnt, '{}' as table_name from {}".format(table_name, table_name)
                for table_name in table_schemas
            ]

            all_row_cnt_results = self.execute_query("\nunion\n".join(all_row_cnt_queries))
            logging.info("Get rows counts for each table over.")
            for result in all_row_cnt_results.rows(as_dict=True):
                table_schemas[result['table_name']].num_rows = result['row_cnt']

            return table_schemas

    def get_connection(self):
        with self._lock:
            if (datetime.now() - self._last_conn_time).total_seconds() > _RECONNECT_SECONDS:
                self._connect_to_server()
            return self._conn

    def _get_conn_str(self):
        return 'DRIVER={ODBC Driver 18 for SQL Server};' + self._conn_string

    def _connect_to_server(self):
        # Resolve 151 error following https://stackoverflow.com/a/58565621
        # TODO: handle each data type following https://learn.microsoft.com/en-us/sql/t-sql/data-types/hierarchyid-data-type-method-reference?view=sql-server-ver15#data-type-conversion
        def handle_hierarchyid(v):
            return str(v)

        def handle_datetimeoffset(dto_value):
            # ref: https://github.com/mkleehammer/pyodbc/issues/134#issuecomment-281739794
            tup = struct.unpack("<6hI2h", dto_value)  # e.g., (2017, 3, 16, 10, 35, 18, 500000000, -6, 0)
            return datetime(tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6] // 1000, timezone(timedelta(hours=tup[7], minutes=tup[8])))

        try:
            self._conn.close()
        except:
            pass

        MANAGED_IDENTITY_ENABLED = os.environ.get("MANAGED_IDENTITY_ENABLED", False)
        if MANAGED_IDENTITY_ENABLED:
            logging.info("Using managed identity to connect to SQL Server")
            credential = ManagedIdentityCredential()
            token = credential.get_token(
                "https://database.windows.net/.default"
            )
            accessToken = bytes(token.token, "utf-8")
            exptoken = b""
            for i in accessToken:
                exptoken += bytes({i})
                exptoken += bytes(1)
            tokenstruct = struct.pack("=i", len(exptoken)) + exptoken
            self.attrs_before = {1256: bytearray(tokenstruct)}

        self._conn = pyodbc.connect(self._get_conn_str(), attrs_before=self.attrs_before)
        self._conn.add_output_converter(-151, handle_hierarchyid)
        self._conn.add_output_converter(-155, handle_datetimeoffset)
        self._last_conn_time = datetime.now()

    def close(self):
        self._conn.close()
    
    def execute_query(self, query: str, **kwargs) -> TableData:
        if not is_readonly_query(query):
            raise Exception("Only read-only query is allowed")

        # logging.info("SQLServer Executor run query: `%s`", query)

        # Do not use as_dict=true as the execution will raise error if there is no naming for select results, for example "select count(*) from ..."
        retry_count = 3
        while retry_count >= 0:
            try:
                cur = self.get_connection().cursor()
                cur.execute(query)
                break
            except pyodbc.Error as pe:
                if pe.args[0] == '08S01':
                    self._connect_to_server()
                    retry_count -= 1
                    logging.error("SQLServer failed to execute query: %s", pe)
                    continue
                raise

        # TODO: add name for empty column result
        col_names = [d[0] for d in cur.description]
        col_types = [d[1].__name__ for d in cur.description]

        # logging.info([d for d in cur.description])
        data = cur.fetchall()

        # convert pyodbc.Row to list
        data = [list(row) for row in data]
        cur.close()

        return TableData(columns=col_names, column_types=col_types, data=data)
