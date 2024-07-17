import requests
from typing import Dict, Union
from ..telemetry import get_correlation_id, CORRELATION_ID

class AzureMLEndpoint:
    def __init__(self, api_url: str, api_key: str=None, deployment_name: str=None) -> None:
        self.api_url = api_url
        self.api_key = api_key
        self.deployment_name = deployment_name
    
    def __call__(self, json=None, **kwargs) -> Union[Dict, bytes]:
        headers = { 'Content-Type':'application/json', 'x-ms-stateful-session-enabled': 'true' }
        request_id = get_correlation_id()
        if request_id:
            headers[CORRELATION_ID] = request_id
        
        if self.api_key:
            headers['Authorization'] =  ('Bearer '+ self.api_key)
        
        if self.deployment_name:
            headers["azureml-model-deployment"] = self.deployment_name
        
        cookies = {}
        if kwargs.get("azureml_sessionid", None):
            cookies["ms-azureml-sessionid"] = kwargs.pop("azureml_sessionid")

        resp = requests.post(
            self.api_url,
            json=json,
            headers=headers,
            cookies=cookies
        )

        result = resp.json()
        if result["status_code"] != 0:
            raise Exception(result.get("error_msg", "Endpoint call exception"))
        
        if kwargs.get("return_azureml_sessionid", False):
            session_id: str = None
            for cookie in resp.cookies:
                if cookie.name == "ms-azureml-sessionid":
                    session_id = cookie.value
                    break
            return result["data"], session_id

        return result["data"]

    @classmethod
    def from_string(cls, conn_string: str) -> "AzureMLEndpoint":
        items = conn_string.split(";")
        assert 1 <= len(items) <= 3
        return AzureMLEndpoint(*items)
