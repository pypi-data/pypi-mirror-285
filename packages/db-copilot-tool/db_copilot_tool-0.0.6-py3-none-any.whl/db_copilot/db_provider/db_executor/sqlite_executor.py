"""
SQLite Database Executor
"""
import os
from typing import OrderedDict, List
from functools import cached_property
import logging
import sqlite3
from typing import Dict

from db_copilot.contract import ColumnSchema, TableSchema, DatabaseType, TableData
from .db_executor import DBExecutor
from db_copilot.telemetry.telemetry import LatencyTracker

logger = logging.getLogger("sqlite_executor")

class SQLiteExecutor(DBExecutor):
    def __init__(self, database: str, is_local: bool=False, tables: List=None) -> None:
        super().__init__(tables)
        self.is_local = is_local
        self.database = database
        self._conn = sqlite3.connect(database, check_same_thread=False)
    
    @property
    def db_type(self) -> DatabaseType:
        return DatabaseType.SQLITE
    
    @cached_property
    def table_schemas(self) -> OrderedDict[str, TableSchema]:
        if not self._tables:
            all_tables_query = "select name from sqlite_master where type='table';"
            self._tables = [x[0] for x in self.execute_query(all_tables_query).rows(as_dict=False)]

        # assign all the table schemas to a variable
        schemas = {
            table_name: self.get_table_schema(table_name)
            for table_name in self._tables
        }

        # identify foreign keys over the variable
        for table_name, table_schema in schemas.items():
            schemas[table_name] = self.identify_foreign_keys(table_name, table_schema, schemas)

        return schemas

    def close(self):
        # Close connection and remove database file
        self._conn.close()
        if not self.is_local and isinstance(self.database, str) and os.path.isfile(self.database):
            os.remove(self.database)

    def get_connection(self):
        return self._conn

    def execute_query(self, query: str) -> TableData:
        cur = self.get_connection().cursor()
        cur.execute(query)
        
        col_names = [d[0] for d in cur.description]
        col_types = ['none' for _ in cur.description]

        data = cur.fetchall()
        cur.close()

        return TableData(columns=col_names, column_types=col_types, data=list(data))

    def get_table_schema(self, table_name: str) -> TableSchema:
        row_cnt_result = self.execute_query(f"select count(1) from {self.sql_dialect.bracket_field_name(table_name)};")
        row_cnt = row_cnt_result.data[0][0]

        sql_query = "PRAGMA table_info({});".format(self.sql_dialect.bracket_field_name(table_name))
        table_info = self.execute_query(sql_query)

        column_schemas: List[ColumnSchema] = []
        primary_columns = []
        for row in table_info.rows(as_dict=True):
            column_schema = ColumnSchema(
                name=row["name"], 
                data_type=row["type"],
            )

            # check if the column name contains "Name" or "ID" and has no duplicate values
            if ("Name" in row["name"] or "ID" in row["name"]) and self.is_unique(table_name, row["name"], row_cnt):
                primary_columns.append(row["name"])
            elif row["pk"]:
                primary_columns.append(row["name"])

            column_schemas.append(column_schema)
        
        if len(primary_columns) == 0:
            logging.warning("No primary column found in table `{}`".format(table_name))

        pk_query = "PRAGMA foreign_key_list({});".format(self.sql_dialect.bracket_field_name(table_name))
        foreign_keys = []
        for row in self.execute_query(pk_query).rows(as_dict=True):
            pk_col, ref_table, ref_col = row['from'], row['table'], row['to']
            foreign_keys.append((pk_col, ref_table, ref_col))

        return TableSchema(
            name=table_name,
            columns=column_schemas,
            primary_key=primary_columns,
            num_rows=row_cnt,
            foreign_keys=foreign_keys
        )
    
    def is_unique(self, table_name: str, column_name: str, table_rows_count:int) -> bool:
        # check if the column has no duplicate values
        count_query = f"select count(distinct {self.sql_dialect.bracket_field_name(column_name)}) from {self.sql_dialect.bracket_field_name(table_name)};"
        count_result = self.execute_query(count_query)
        count = count_result.data[0][0]
        return count == table_rows_count
    
    def is_subset(self, table_name: str, column_name: str, other_table: str, other_column: str) -> bool:
        # check if the value set of other_column is subset of the value set of column_name
        subset_query = f"select count(*) from {self.sql_dialect.bracket_field_name(other_table)} where {self.sql_dialect.bracket_field_name(other_column)} not in (select {self.sql_dialect.bracket_field_name(column_name)} from {self.sql_dialect.bracket_field_name(table_name)});"
        subset_result = self.execute_query(subset_query)
        subset_count = subset_result.data[0][0]
        return subset_count == 0
    
    def identify_foreign_keys(self, table_name: str, table_schema: TableSchema, schemas: Dict[str, TableSchema]) -> TableSchema:
        try:
            with LatencyTracker() as t:
                # Iterate over each column in the table
                for col_schema in table_schema.columns:
                    col = col_schema.name
                
                    # Check this column against primary keys in other tables
                    for other_table, other_schema in schemas.items():
                        if other_table != table_name:
                            for primary_col in other_schema.primary_key:
                                if self.is_subset(other_table, primary_col, table_name, col):
                                    # Add it as a foreign key relationship
                                    table_schema.foreign_keys.append(("[{}].[{}]".format(table_name, col), other_table, primary_col))
                                    logging.warning("Foreign key found between table `{}`.{} and table `{}`.{}".format(table_name, col, other_table, primary_col))

            logger.info(f"Identifying Foreign keys executed for table name {table_name} in {t.duration} seconds")
        except Exception as e:
            # eat up the exception if there is any failure.
            logger.error(f"An error occurred while identifying foreign keys for table name {table_name}: {e}")  

        return table_schema




