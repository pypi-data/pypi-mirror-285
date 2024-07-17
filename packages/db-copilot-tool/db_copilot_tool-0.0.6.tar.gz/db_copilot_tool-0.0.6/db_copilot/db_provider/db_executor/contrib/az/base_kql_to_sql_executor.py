import logging
import requests
import re

from .az_utils import kusto_table_to_py_table

from db_copilot.contract import DatabaseType, TableData, TableSchema, ColumnSchema, SQLDialect
from db_copilot.db_provider.db_executor.kusto_executor import KustoExecutor

logger = logging.getLogger("base_kql_to_sql_executor")

class WrongQueryError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class BaseKqlToSqlExecutor(KustoExecutor):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.kql_dialect = SQLDialect.from_db_type(DatabaseType.KUSTO)
    
    @property
    def db_type(self) -> str:
        return DatabaseType.SQLSERVER
    
    @property
    def _cluster_uri(self) -> str:
        return self._conn_string.split(';')[0].strip()

    
    def _create_kusto_client(self, kcsb):
        try:
            import azure.kusto.data
            
        except ImportError:
            raise ValueError(
                "Could not import required python package. "
                "Please install dbcopilot with `pip install dbcopilot[extensions] ...` "
            )
        class _MyKustoClient(azure.kusto.data.KustoClient):
            def get_access_token(self2):
                return self2._aad_helper.token_provider.get_token()
        return _MyKustoClient(kcsb)
    
    def _strip_sql_comments(self, query: str):
        return re.sub(r'^\s*--.*', '', query, flags=re.MULTILINE).strip()

    def _is_sql(self, query: str):
        return re.search(r'^select\s', self._strip_sql_comments(query).lstrip('\r\n ('), flags=re.IGNORECASE)
    
    def _process_sql(self, sql: str) -> str:
        # NEWID() is not supported by sql2kql translation
        sql = re.sub(r'\bORDER\s+BY\s+NEWID\(\)\b', 'ORDER BY RAND()', sql, flags=re.MULTILINE | re.IGNORECASE).strip()
        return sql

    def _sql_to_kql(self, sql: str, db: str = ""):
        client = self.get_connection()
        """call Kusto's rest api to convert SQL to KQL"""
        logger.info("sql_to_kql: %s", sql)
        sql = self._process_sql(self._strip_sql_comments(sql))
        access_token = client.get_access_token()
        if not db:
            db = self._database
        if not access_token:
            client.execute(db, ".show tables | project TableName")
            access_token = client.get_access_token()
        if not access_token:
            raise Exception(
                "cannot get access token from KustoClient for sql2kql translation"
            )
        headers = {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "authorization": "{token_type} {access_token}".format(**access_token)
            if "access_token" in access_token.keys()
            else "{tokenType} {accessToken}".format(**access_token),
            "cache-control": "no-cache",
            "content-type": "application/json; charset=UTF-8",
            "pragma": "no-cache",
            "sec-ch-ua": '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
        }
        body = {
            "db": db,
            # https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/sqlcheatsheet
            "csl": f"--\nEXPLAIN\n{sql}",
            "properties": {
                "Options": {
                    "servertimeout": "00:04:00",
                    "queryconsistency": "strongconsistency",
                    "query_language": "sql",
                    "request_readonly": False,
                    "request_readonly_hardline": False,
                }
            },
        }

        query_uri = f"{self._cluster_uri}/v2/rest/query"
        response = requests.post(
            query_uri,
            json=body,
            headers=headers,
        )
        data = response.json()
        if "error" in data and data["error"]:
            if "innererror" in data["error"] and \
                "@message" in data["error"]["innererror"] and \
                "code" in data["error"]["innererror"] and \
                data["error"]["innererror"]["code"] in ["SQL->CSL translation error"]:
                logger.error("sql_to_kql.error %s", data["error"]["innererror"]["@message"])
                raise WrongQueryError(data["error"]["innererror"]["@message"])
            logger.error("sql_to_kql.error %s", data["error"]["message"])
            raise WrongQueryError(data["error"]["message"])
        data = [
            a["Rows"][0]
            for a in data
            if a["FrameType"] == "DataTable" and a["TableKind"] == "PrimaryResult"
        ]
        logger.info("sql_to_kql.result %s", data[0][0])
        return data[0][0]

    def _execute_kql(self, query: str, **kwargs) -> TableData:
        return super().execute_query(query, **kwargs)
    
    def execute_query(self, query: str, **kwargs) -> TableData:
        if not self._is_sql(query):
            # come from kusto grounding
            return self._execute_kql(query=query, **kwargs)
        kql = self._sql_to_kql(sql=query)
        return kusto_table_to_py_table(self._execute_kql(kql, **kwargs))
