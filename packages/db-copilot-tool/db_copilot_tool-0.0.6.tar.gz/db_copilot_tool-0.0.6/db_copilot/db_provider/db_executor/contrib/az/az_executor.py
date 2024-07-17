import logging
import re
from typing import Optional, List
import uuid
from .az_utils import AzRequest, tabledata_to_kql_datatable, kusto_table_to_py_table

from db_copilot.contract import TableSchema, DatabaseType, TableData
from .base_kql_to_sql_executor import BaseKqlToSqlExecutor

logger = logging.getLogger("azure_executor")

_SAMPLES_COUNT_TO_KEEP_IN_KUSTO = 10


class AzExecutor(BaseKqlToSqlExecutor):
    """
    @Description: A executor which take your Azure Resource Graph and Log Analytics Workspace as datasource and enable LLM's interaction via TSQL query.
    @Author: Dashi (alias: shida)
    """
    def __init__(self,
                 conn_string: str,
                 database: str,
                 la_table_mappings: dict,
                 rg_table_mappings: dict,
                 la_monitor_resource_type: str,
                 database_version: Optional[str] = None,
                 recreate_kusto_db: bool = False,
                 subscription_id: str = '',
                 tables: Optional[List[str]] = None,
                 **kwargs) -> None:
        super().__init__(
            conn_string=conn_string,
            database=database,
            database_version=database_version,
            tables=list([t for t in
                set(list(la_table_mappings.keys()) + list(rg_table_mappings.keys())) if not tables or t in tables]),
            **kwargs)
        self._recreate_kusto_db = recreate_kusto_db
        self._subscription_id = subscription_id
        assert la_table_mappings is not None
        assert rg_table_mappings is not None
        assert len(set(list(la_table_mappings.keys()) + list(rg_table_mappings.keys()))) == len(la_table_mappings) + \
            len(rg_table_mappings), "There mustn't be duplicated keys between LA/RG table mappings"
        assert la_monitor_resource_type is not None
        self._la_table_mappings = la_table_mappings
        self._rg_table_mappings = rg_table_mappings
        self._la_monitor_resource_type = la_monitor_resource_type
        # TODO: pass AzRequest instance per query, or, make lifetime of AzExecutor per session
        self._az_executor = AzRequest.with_test_az_auth()

    def get_table_schemas(self):
        self._prepare(force_recreate=self._recreate_kusto_db)
        tables = super().get_table_schemas()
        # hide those internal tables starts with _
        tables_to_hide = []
        for table in tables:
            if table.startswith('_'):
                tables_to_hide.append(table)
        for table in tables_to_hide:
            tables.pop(table)
        return tables

    def get_table_schemas_security_database(self):
        self._prepare(force_recreate=self._recreate_kusto_db)
        return super().get_table_schemas_security_database()

    @property
    def db_type(self) -> str:
        return DatabaseType.SQLSERVER

    def _prepare(self, force_recreate: bool = False):
        self._connect_to_server()
        existing_tables = [row['TableName'] for row in self._client.execute_mgmt(self._database,
            '.show tables | project TableName').primary_results[0].rows]
        existing_tables.sort()
        logger.info('existing_tables %s', existing_tables)
        if not force_recreate:
            expected_tables = list(
                set(list(self._la_table_mappings.keys()) + list(self._rg_table_mappings.keys())))
            expected_tables.sort()
            logger.info('expected_tables %s', expected_tables)
            if existing_tables == expected_tables:
                # all tables exists, just return
                return
        logger.info('recreating Kusto schema, drop all existing_tables')

        # generate kusto tables
        if existing_tables:
            self._client.execute_mgmt(self._database,
                f".drop tables ({', '.join(existing_tables)}) ifexists")

        for table_name in self._la_table_mappings:
            la_query = self._la_table_mappings[table_name]['query'].strip()
            logger.info('creating LA table %s as %s', table_name, la_query)
            samples = self._execute_kql_query(
                query=f"{la_query} | take {_SAMPLES_COUNT_TO_KEEP_IN_KUSTO}")
            self._client.execute_mgmt(self._database,
                f".set {table_name} <| {tabledata_to_kql_datatable(samples)}")

        for table_name in self._rg_table_mappings:
            rg_query = self._rg_table_mappings[table_name]['query'].strip()
            logger.info('creating RG table %s as %s', table_name, rg_query)
            samples = self._execute_rg(
                query=f"{rg_query} | take {_SAMPLES_COUNT_TO_KEEP_IN_KUSTO}",
                columns=self._rg_table_mappings[table_name]['columns'])
            logging.info(f".set {table_name} <| {tabledata_to_kql_datatable(samples)}")
            self._client.execute_mgmt(self._database,
                f".set {table_name} <| {tabledata_to_kql_datatable(samples)}")

    def _execute_rg(self, query: str, columns: Optional[dict] = None) -> TableData:
        return self._az_executor.call_rg(query=query, columns=columns)

    def _execute_la(self, query: str) -> TableData:
        return self._az_executor.call_la(query=query, monitor_resource_type=self._la_monitor_resource_type, subscription_id=self._subscription_id)
    
    def _query_contains_table(self, query: str, table: str) -> bool:
        return self._count_table_occurrence_in_query(query=query, table=table) != 0
    
    def _count_table_occurrence_in_query(self, query: str, table: str) -> int:
        table_regex_escaped = re.escape(table)
        # find ["table"] ['table'] [table] or xxx.table or table.xxx or [space]table[space] or (table)
        return len(re.findall(
            r'(' +
            r'\["' + table_regex_escaped + r'"\]' +
            r"|\['" + table_regex_escaped + r"'\]" +
            r'|\[' + table_regex_escaped + r'\]' +
            r'|(^|\.|\s|\()' + table_regex_escaped + r'(\)|\s|\.|$)' +
            r')', query, flags=re.MULTILINE))

    def _count_tables_occurrence_in_query(self, query: str, tables: list) -> int:
        result = 0
        for table in tables:
            result += self._count_table_occurrence_in_query(query=query, table=table)
        return result

    def _reaplce_table_in_query(self, query: str, table: str, replacement: str) -> str:
        # [table]
        result = re.sub(r'\[' + re.escape(table) + r'\]', replacement, query)
        # ['table'] & ["table"]
        result = re.sub(r'\["' + re.escape(table) + r'"\]', replacement, result)
        result = re.sub(r"\['" + re.escape(table) + r"'\]", replacement, result)
        # table
        result = re.sub(r'\b' + re.escape(table) + r'\b', replacement, result)
        return result
    
    def _insert_let_alias_to_query(self, query, alias) -> str:
        queries = query.strip().split(';')
        queries[-1] = f"let {alias}={queries[-1].strip()}"
        return ';'.join(queries).strip(';').replace("__random__", uuid.uuid4().hex)


    def _execute_kql_query(self, query: str, **kwargs)-> TableData:
        kql = query
        logger.info('execute_query kql %s', kql)
        kql_prefixes = []
        rg_tables = [table for table in self._rg_table_mappings if self._query_contains_table(kql, table)]
        la_tables = [table for table in self._la_table_mappings if self._query_contains_table(kql, table)]
        if not rg_tables:
            # LA shortcut mode: there are no RG query, execute kql directly in LA
            # example query:
            #   let la_table=Events | where ... | project ...
            #   la_table | count
            virtual_table_definiation_set = {}
            _tmp_query = query
            logging.info('self._la_table_mappings %s', self._la_table_mappings)
            while True:
                find_new_virtual_table = False
                for table_name in self._la_table_mappings:
                    if self._query_contains_table(_tmp_query, table_name) and table_name not in virtual_table_definiation_set:
                        virtual_table_definiation_set[table_name] = True
                        _tmp_query = self._reaplce_table_in_query(_tmp_query, table_name, self._la_table_mappings[table_name]['query'])
                        logging.info('_tmp_query %s===================== \n\n%s\n\n', table_name, _tmp_query)
                        find_new_virtual_table = True
                        kql_prefixes.insert(
                            0,
                            f"{self._insert_let_alias_to_query(self._la_table_mappings[table_name]['query'], table_name)};")
                        break
                if not find_new_virtual_table:
                    break
            new_kql = '\n'.join(kql_prefixes) + '\n' + kql
            logger.info('execute_query la_mode_kql %s', new_kql)
            return self._execute_la(new_kql)
        elif not la_tables and self._count_tables_occurrence_in_query(kql, rg_tables) <= 2:
            # RG shortcut mode:
            # example query:
            #   rg_table1 | join rg_table2 | where ... =>
            #   (resources | where ...) | join (resources | where) | where ...

            # TODO: catch exception and fallback to full mode
            new_kql = kql
            for table_name in rg_tables:
                new_kql = self._reaplce_table_in_query(new_kql, table_name, self._rg_table_mappings[table_name]['query'].strip())
            
            logger.info('execute_query rg_mode_kql %s', new_kql)
            return self._execute_rg(new_kql)
    
        # full mode: fetch all LA & RG and form a query and execute it in Kusto
        # - mixed of LA & RG query
        # - RG don't support joining the same table twice
        # example query:
        #   let rg_table=datatable(...)[...];
        #   let la_table=datatable(...)[...];
        #   rg_table | join la_table |...
        for table_name in rg_tables:
            rg_result = self._execute_rg(
                query=self._rg_table_mappings[table_name]['query'].strip(),
                columns=self._rg_table_mappings[table_name]['columns'])
            kql_prefixes.append(
                f"let {table_name}={tabledata_to_kql_datatable(rg_result)};\n")
        for table_name in la_tables:
            la_result = self._execute_kql_query(
                query=self._la_table_mappings[table_name]['query'].strip())
            kql_prefixes.append(
                f"let {table_name}={tabledata_to_kql_datatable(la_result)};\n")
        new_kql = '\n'.join(kql_prefixes) + '\n' + kql
        logger.info('execute_query full_mode_kql %s', new_kql)
        return self._execute_kql(new_kql)

    def execute_query(self, query: str, **kwargs) -> TableData:
        if not self._is_sql(query):
            logger.info('execute_query kql %s', query)
            # the request come from kusto grounding
            return self._execute_kql(query=query, **kwargs)
        logger.info('execute_query sql %s', query)
        kql = self._sql_to_kql(sql=query)
        return kusto_table_to_py_table(self._execute_kql_query(query=kql, **kwargs))
        
