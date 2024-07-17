"""
CosmosDB Executor
"""
from typing import OrderedDict
from functools import cached_property
import logging

from db_copilot.contract import ColumnSchema, TableSchema, DatabaseType, TableData
from .db_executor import DBExecutor


logger = logging.getLogger("cosmos_executor")


def list_all_containers(client):
    for db in client.list_databases():
        db_id = db['id']
        db = client.get_database_client(db_id)
        for container in db.list_containers():
            container_id = container['id']
            yield '{}.{}'.format(db_id, container_id)


class CosmosExecutor(DBExecutor):
    def __init__(self, **kwargs) -> None:
        super().__init__(kwargs['tables'])
        self.db = kwargs['db']
        self.container = kwargs['container']
        self.url = kwargs['url']
        self.key = kwargs['key']
        self.get_connection()
    
    @property
    def db_type(self) -> DatabaseType:
        return DatabaseType.COSMOS
    
    @cached_property
    def table_schemas(self) -> OrderedDict[str, TableSchema]:
        res = {table_name: self.get_table_schema(table_name) for table_name in list_all_containers(self.client)}
        return res

    def close(self):
        pass
    
    def get_connection(self):
        try:
            from azure.cosmos import CosmosClient
            self.client = CosmosClient(self.url, credential=self.key)
        except ImportError:
            raise ImportError("Please install azure-cosmos to use CosmosDBExecutor")

    def _get_table_sample_query(self, *args, **kwargs):
        return 'SELECT TOP 1 * FROM c'

    def execute_query(self, query: str) -> TableData:
        database = self.client.get_database_client(self.db)
        container = database.get_container_client(self.container)
        data = []
        keys = []
        for r in container.query_items(query=query, enable_cross_partition_query=True):
            keys = list(r.keys())
            data.append([])
            for key in keys:
                data[-1].append(r[key])
        return TableData(columns=keys, column_types=['str' for _ in range(len(keys))], data=data)


    def get_table_schema(self, table_name: str) -> TableSchema:

        table_name_items = table_name.split('.')
        db_id = table_name_items[0]
        container_id = table_name_items[1]
        database = self.client.get_database_client(db_id)
        container = database.get_container_client(container_id)

        column_schemas = {}
        num_rows = 0

        primary_key = []
        for r in container.query_items(query='SELECT * FROM c', enable_cross_partition_query=True):
            num_rows += 1
            primary_key.append(r['id'])
            for k, _ in r.items():
                if k not in column_schemas:
                    column_schemas[k] = ColumnSchema(name=k, data_type='str')

        return TableSchema(
            name=table_name, 
            columns=list(column_schemas.values()),
            num_rows=num_rows,
            primary_key=primary_key,
            foreign_keys=[]
        )
