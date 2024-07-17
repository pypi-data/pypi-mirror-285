import json
import time
import urllib.request
from typing import List

import numpy as np

from ..contract.embedding_core import EmbeddingModel


class AMLEmbeddings(EmbeddingModel):
    def __init__(self, endpoint, api_key, deployment_name='blue'):
        self.endpoint = endpoint
        api_key = api_key
        self.headers = {'Content-Type': 'application/json', 'Authorization': (
            'Bearer ' + api_key), 'azureml-model-deployment': deployment_name}
        super().__init__()

    def get_embeddings(self, texts: List[str], **kwargs) -> List:
        data = {"sentences": texts}
        body = str.encode(json.dumps(data))
        req = urllib.request.Request(self.endpoint, body, self.headers)
        n_retry = kwargs.get('n_retry', 3)
        retry_delay_seconds = kwargs.get('retry_delay_seconds', 1)
        retries = 0
        while retries < n_retry:
            try:
                response = urllib.request.urlopen(req)
                result = response.read()
                embeddings = json.loads(result)
                break
            except Exception as e:
                retries += 1
                if retries >= n_retry:
                    raise e
                else:
                    time.sleep(retry_delay_seconds)
        return np.vstack(embeddings, dtype=np.float32)
