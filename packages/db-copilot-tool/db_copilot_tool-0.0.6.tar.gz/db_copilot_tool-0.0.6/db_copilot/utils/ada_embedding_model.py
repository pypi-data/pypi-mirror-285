from functools import lru_cache
import time
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import numpy.typing as npt
import requests
from db_copilot.telemetry import get_logger
from db_copilot.telemetry.telemetry import LatencyTracker
logger = get_logger("ada_embedding_model")

from db_copilot.contract import EmbeddingModel

ADA_EMBEDDING_SIZE = 1536
ADA_MAX_CHUNK_SIZE = 1900


def sync_post(url: str, headers: Dict[str, Any], body: Dict[str, Any]):
    with LatencyTracker() as t:
        resp = requests.post(url, headers=headers, json=body)
    logger.info(f"POST {url} executed in {t.duration} seconds")
    resp.raise_for_status()
    return resp.json()


def most_similar_topk(x: npt.NDArray[np.float32], M: npt.NDArray[np.float32], k: int) -> npt.NDArray:
    dot_product = np.dot(x, M.T)
    norm_a = np.linalg.norm(x)
    norm_b = np.linalg.norm(M, axis=1)
    score = dot_product / (norm_a * norm_b)
    topk_idx = np.argsort(score)[::-1][:k]
    return topk_idx


def find_top_matches(query_embedding: npt.NDArray, batch_embeddings: npt.NDArray, k: int) -> List[int]:
    most_similar_doc_idx = most_similar_topk(
        query_embedding, batch_embeddings, k)
    return list(most_similar_doc_idx)


def sync_query_ada(all_queries: List[str], bs: int, endpoint_url: str, deployment: str, api_key: str = None,
                   ignore_errors: bool = False, max_workers: int = 4, n_retry: int = 3, retry_delay_seconds: float = 1) -> npt.NDArray:
    batch_embed_list = []
    dim_size = ADA_EMBEDDING_SIZE  # HARDCODED ADA EMBEDDING SIZE
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for batch_idx in range(0, len(all_queries), bs):
            batch = all_queries[batch_idx:batch_idx+bs]
            future = executor.submit(generate_embedding_using_endpoint,
                                            endpoint_url, api_key, deployment, batch, n_retry, retry_delay_seconds)
            futures.append(future)
        for batch_idx, future in enumerate(futures):
            try:
                batch_embeddings = future.result()
            except Exception as e:
                error_str = f"Error in generating embedding for batch {batch_idx} due to {e}"
                if not ignore_errors:
                    raise Exception(error_str)
                else:
                    print(f"WARN: (ERROR IGNORED) {error_str}.\n Please check your url, key and input data for encoding")
                batch_embeddings = np.ones((bs, dim_size))
            batch_embed_list.append(batch_embeddings)
    batch_embeddings = np.concatenate(batch_embed_list, axis=0)
    return batch_embeddings


@lru_cache
def sync_query_ada_single(query: str, bs: int, endpoint_url: str, api_key: str, deployment: str,
                   ignore_errors: bool = False) -> npt.NDArray:
    return sync_query_ada([query], bs, endpoint_url, api_key, deployment, ignore_errors)


def prepare_headers_input(api_key: str, deployment: str, input_texts: List[str]) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    headers = {
        'Content-Type': 'application/json', 'Authorization': ('Bearer ' + api_key),
        'ocp-apim-subscription-key': api_key,
        'api-key': api_key,
        "azureml-model-deployment": deployment
    }
    input_dict = dict()
    input_dict["input"] = [text for text in input_texts]
    return headers, input_dict


def process_response(response_json: Dict[str, Any]) -> List[npt.NDArray]:
    batch_call = response_json
    if "data" not in batch_call:
        raise Exception(
            f"Call to endpoint failed. Response was {batch_call}.")
    batch_call = batch_call["data"]
    fs_output = [
        np.array(batch_call_sample["embedding"], dtype=np.float32)
        for batch_call_sample in batch_call
    ]
    return fs_output


def generate_embedding_using_endpoint(endpoint_url: str, deployment: str,
                                      input_texts: List[str], api_key: str = None, n_retry: int=3, retry_delay_seconds: float =1) -> List[npt.NDArray]:
    headers, input_dict = prepare_headers_input(
        api_key, deployment, input_texts)
    retries = 0  
    while retries < n_retry:
        try:
            response_json = sync_post(endpoint_url, headers, input_dict)
            break
        except Exception as e:
            retries += 1
            if retries >= n_retry:
                raise e
            else:
                time.sleep(retry_delay_seconds)
    return process_response(response_json)


class OpenaiEmbeddings(EmbeddingModel):
    def __init__(self,
                 endpoint_url: str,
                 api_key: str,
                 model: str,
                 max_workers: int = 1,
                 n_retry: int = 3,
                 retry_delay_seconds: float = 1
                 ) -> None:
        self.endpoint_url = endpoint_url
        self.api_key = api_key
        self.model = model
        self.max_workers = max_workers
        self.n_retry = n_retry
        self.retry_delay_seconds = retry_delay_seconds
        super().__init__()

    def get_embeddings(self, texts: List[str], **kwargs) -> List:
        """Embed search docs."""
        with LatencyTracker() as t:
            emb_vectors = sync_query_ada(texts,
                                     bs=kwargs.get('batch_size', 1),
                                     endpoint_url=self.endpoint_url,
                                     api_key=self.api_key,
                                     deployment=self.model,
                                     max_workers=self.max_workers,
                                     n_retry=self.n_retry,
                                     retry_delay_seconds=self.retry_delay_seconds
                                    )
        logger.info(f"Embedding for {len(texts)} texts generated in {t.duration} seconds")
        return emb_vectors


    def embed_query(self, text: str) -> List[float]:
        return self.get_embeddings([text])[0]