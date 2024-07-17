import logging
import json
import re
import time
from typing import List, Optional
from abc import ABC, abstractmethod
import datetime
from db_copilot.contract import TableData

logger = logging.getLogger()
logger.setLevel(logging.INFO)


_AUTH_METHOD_TEST_AZ = 'test_az_auth'


class AzRequest(ABC):
    auth_method: str

    @classmethod
    def with_test_az_auth(cls) -> "AzRequest":
        return _TestAzRequest()

    def get_resource_ids_with_insights(self, type: str = '') -> List[str]:
        logging.info('get_resource_ids_with_insights type=%s', type)
        query_type = f"| where type =~ {json.dumps(type)}" if type else ''
        result = self.call_rg(f"""
            insightsresources
            | project resource_id=replace(@'/providers/Microsoft.Insights/.*', @'', id)
            | join kind=inner resources on $left.resource_id == $right.id
            {query_type} | project id
        """, {"id": "string"})
        return [row[0] for row in result.data]

    def get_la_workspace_ids(self, monitor_resource_type: str = '', filter_by_resource_id_existence: bool = True, filter_by_workspace_id_existence: bool = True) -> List[str]:
        # logging.info('get_la_workspace_ids monitor_resource_type=%s filter_by_resource_id_existence=%s', monitor_resource_type, filter_by_resource_id_existence)
        query_filter_by_resource_id_existence = ''
        if filter_by_resource_id_existence:
            res_ids = [id.lower() for id in self.get_resource_ids_with_insights(type=monitor_resource_type)]
            query_filter_by_resource_id_existence = f"| where resource_id in ({json.dumps(res_ids).strip('[]')})"
        query = f"""
            insightsresources
            | where type =~ 'microsoft.insights/datacollectionruleassociations'
            | where id contains '/providers/Microsoft.Insights/'
            | project resource_id=tolower(replace(@'/providers/Microsoft.Insights/.*', @'', id)), dataCollectionRule_id=tostring(properties['dataCollectionRuleId'])
            {query_filter_by_resource_id_existence} | join kind=inner ( 
                resources
                | where type == "microsoft.insights/datacollectionrules"
                | project dataCollectionRule_id = id, dataCollectionRule_properties=properties
            ) on dataCollectionRule_id
            | extend workspaces=dataCollectionRule_properties['destinations']['logAnalytics']
            | mv-expand workspaces
            | extend workspace_id=tostring(workspaces['workspaceResourceId'])
            | distinct workspace_id
        """
        result = self.call_rg(query, {"workspace_id": "string"})
        # logging.info('get_la_workspace_ids => %s => %s', query, result)
        workspace_ids = [row[0] for row in result.data]
        
        if filter_by_workspace_id_existence:
            result = self.call_rg(f"""
                resources | where type =~ "microsoft.operationalinsights/workspaces" | project id | where id in ({json.dumps(workspace_ids).strip('[]')})
            """, {"id": "string"})
            workspace_ids = [row[0] for row in result.data]
        
        return workspace_ids

    def get_la_workspace_customerIds(self, law_ids: list) -> List[str]:
        result = self.call_rg(f"""
            resources |
            where type == "microsoft.operationalinsights/workspaces"
            | where id in ({json.dumps(law_ids).strip('[]')})
            | project customerId=properties['customerId']
        """, {"customerId": "string"})
        return [row[0] for row in result.data]

    @abstractmethod
    def call_rg(self, query: str, columns: dict) -> TableData:
        pass

    @abstractmethod
    def call_la(self, query: str, monitor_resource_type: str = '') -> TableData:
        pass


def _call_az(*args, **kwargs):
    logger.debug(f"query {args}")
    
    try:
        import az.cli
        
    except ImportError:
        raise ValueError(
            "Could not import required python package. "
            "Please install az.cli with `pip install az.cli` "
        )
    exit_code, result, logs = az.cli.az(*args, **kwargs)
    if exit_code != 0:
        logger.error(logs)
    return result

class _TestAzRequest(AzRequest):
    def __init__(self):
        super().__init__()
        self.auth_method = _AUTH_METHOD_TEST_AZ
        self._cache = {}
        self._cacheTime = {}


    def call_rg(self, query: str, columns: Optional[dict] = None) -> TableData:
        escaped_graph_query = query.replace("\\", "\\\\").replace("\"", "\\\"")
        res = _call_az(f'graph query --graph-query "{escaped_graph_query}" ')
        result = res
        while "skip_token" in res.keys() and res["skip_token"] != None:
            res = _call_az(
                f"graph query --graph-query \"{escaped_graph_query}\" --skip-token \"{res['skip_token']}\""
            )
            result["data"] += res["data"]
        # logging.info('call_rg.raw_result %s', result["data"])
        if columns is None:
            # guess from result json
            if len(result["data"]):
                first_row = result["data"][0]
                columns_list = [key for key in first_row]
                for auto_append_column in ['resourceGroup']:
                    if len(columns_list) > 1 and columns_list[-1] == auto_append_column and not re.search("\\b" + re.escape(auto_append_column) + "\\b", query):
                        columns_list = columns_list[:-1]
                column_types_list = [py_object_to_kusto_type(first_row[key]) for key in columns_list]
                logger.info('rg_no_column_info guessed %s => %s %s', query, columns_list, column_types_list)
            else:
                columns_list = [TableData.empty_column_info_name()]
                column_types_list = [TableData.empty_column_info_type()]
                logger.warn('rg_no_column_info empty result %s', query)
        else:
            columns_list = []
            column_types_list = []
            for key in columns:
                columns_list.append(key)
                column_types_list.append(columns[key])
        rows = []
        for entry in result["data"]:
            row = []
            for key in columns_list:
                row.append(entry[key])
            rows.append(row)
        # logging.info('call_rg.rows %s', rows)
        return TableData(columns=columns_list, column_types=column_types_list, data=rows)

    def call_la(self, query: str, monitor_resource_type: str = '', subscription_id: str = '') -> TableData:
        if not subscription_id:
            subscription_id = _call_az("account show")["id"]
            logger.info(f"call_la: get default az subscription id: {subscription_id}")
        la_workspace_ids_cache_key = f"{monitor_resource_type}"
        if la_workspace_ids_cache_key in self._cacheTime.keys() and self._cacheTime[la_workspace_ids_cache_key] > datetime.datetime.now() - datetime.timedelta(minutes=30):
            la_workspace_ids = self._cache[la_workspace_ids_cache_key]
        else:
            la_workspace_ids = self.get_la_workspace_ids(
                monitor_resource_type=monitor_resource_type)
            if la_workspace_ids:
                self._cache[la_workspace_ids_cache_key] = la_workspace_ids
                self._cacheTime[la_workspace_ids_cache_key] = datetime.datetime.now()
        if not la_workspace_ids:
            raise Exception(f'cannot find any LA workspace ids with monitor_resource_type={monitor_resource_type}')
        start_time = time.perf_counter()
        # https://learn.microsoft.com/en-us/rest/api/loganalytics/dataaccess/query/execute?tabs=HTTP#cross-workspace
        headers = {
            "x-ms-client-request-info": "Query",
        }
        queries = {
            "timespan": "PT4H",
            "scope": "hierarchy"
        }
        body = {
            "query": query,
            "options": {"truncationMaxSize": 67108864},
            "maxRows": 30001,
            "workspaceFilters": {"regions": []},
            "workspaces": la_workspace_ids,
        }
        cmd_headers = json.dumps(headers).replace(
            "\\", "\\\\").replace("\"", "\\\"")
        cmd_queries = json.dumps(queries).replace(
            "\\", "\\\\").replace("\"", "\\\"")
        cmd_body = json.dumps(body).replace("\\", "\\\\").replace("\"", "\\\"")
        law_customerIds = self.get_la_workspace_customerIds(la_workspace_ids)
        if not law_customerIds:
            raise Exception(f'cannot find any LA workspace customer ids with la_workspace_ids={la_workspace_ids}')

        cmd = f'rest --method post --url \'https://api.loganalytics.io/v1/workspaces/{law_customerIds[0]}/query\' --uri-parameters "{cmd_queries}" --headers "{cmd_headers}" --body "{cmd_body}"'
        logging.info(f"call:LA {cmd}")
        res = _call_az(cmd)
        la_result = res["tables"][0]
        col_names = [c['name'] for c in la_result['columns']]
        col_types = [c['type'] for c in la_result['columns']]
        data = [row for row in la_result['rows']]
        
        end_time = time.perf_counter()

        elapsed_time = end_time - start_time
        logging.info("call_la finished: [%s rows returned in %ss] %s", len(data), elapsed_time, query)
        return TableData(columns=col_names, column_types=col_types, data=data)


def tabledata_to_kql_datatable(tabledata: TableData) -> str:
    assert isinstance(tabledata.data, list)
    i = 0
    kql_header = []
    for column in tabledata.columns:
        column_type = tabledata.column_types[i]
        kql_header.append(f"{column}: {column_type}")
        i += 1
    
    # kusto's string type doesn't accept null
    data_list = []
    for row in tabledata.data:
        index = 0
        for value in row:
            kusto_data_type = tabledata.column_types[index]
            
            if value is None:
                if kusto_data_type == 'string':
                    value_kusto = ''
                else:
                    value_kusto = f'{kusto_data_type}(null)'
            else:
                value_kusto = json.dumps(value)
            data_list.append(value_kusto)
            index += 1
    
    return f"datatable ({', '.join(kql_header)}) [{','.join(data_list)}]"

_KUSTO_TYPE_TO_PY_TYPE = {
    "bool": "bool",
    "datetime": "datetime",
    "int": "int",
    "string": "str",
    "real": "float",
    "decimal": "str",
    "dynamic": "str",
}

def kusto_type_to_py_type(kusto_type: str) -> str:
    if kusto_type in _KUSTO_TYPE_TO_PY_TYPE.keys():
        return _KUSTO_TYPE_TO_PY_TYPE[kusto_type]
    return 'str'

def kusto_table_to_py_table(kusto_table: TableData) -> TableData:
    kusto_table.column_types = [kusto_type_to_py_type(c) for c in kusto_table.column_types]
    return kusto_table

def py_object_to_kusto_type(obj) -> str:
    if obj is None:
        return 'dynamic'
    t = type(obj)
    if t is bool:
        return 'bool'
    if t is datetime.datetime or t is datetime.date:
        return 'datetime'
    if t is int:
        return 'int'
    if t is str:
        return 'string'
    if t is float:
        return 'real'
    if t is complex:
        return 'decimal'
    return 'dynamic'