import os
from typing import List, Dict, Iterator
import logging
from functools import lru_cache
import multiprocessing
import numpy as np

from db_copilot.contract import EmbeddingModel
from db_copilot.db_provider.utils import StopWatcher
from huggingface_hub import snapshot_download


def dependable_import():
    try:
        import onnxruntime
        from transformers import AutoTokenizer
        from transformers.tokenization_utils_fast import PreTrainedTokenizerFast

        # from transformers.utils.hub import cached_file
        from db_copilot.db_provider.utils import cached_path, DEFAULT_CACHE_PATH
    except ImportError as e:
        raise ValueError(
            f"Could not import required python package ({e.msg}). Please install dbcopilot with `pip install dbcopilot[extensions] ...` "
        )
    return onnxruntime, AutoTokenizer, PreTrainedTokenizerFast, cached_path, DEFAULT_CACHE_PATH


def pad_values_as_numpy(
    input_values: List[np.ndarray],
    padding_value: int = 0,
    dtype=np.int64,
    max_length: int = None,
):
    seq_length = max(len(x) for x in input_values)
    batched_input = np.full((len(input_values), seq_length), padding_value, dtype=dtype)

    for i, array in enumerate(input_values):
        batched_input[i, : len(array)] = array

    if max_length:
        batched_input = batched_input[:, :max_length]

    return batched_input


def fetch_by_indices(array: List, indices: List[int]) -> List:
    return [array[i] for i in indices]


class ORTEmbeddingModel(EmbeddingModel):
    def __init__(self, model_name_or_path: str, is_hf: bool=False) -> None:
        (
            self.onnxruntime,
            self.AutoTokenizer,
            self.PreTrainedTokenizerFast,
            self.cached_path,
            DEFAULT_CACHE_PATH,
        ) = dependable_import()

        if model_name_or_path.startswith("https://"):
            model_name_or_path = self.cached_path(
                model_name_or_path, extract_compressed_file=True
            )
        elif is_hf:
            _model_name_or_path = model_name_or_path
            model_name_or_path = os.path.join(DEFAULT_CACHE_PATH, 'distillroberta.onnx')
            os.makedirs(model_name_or_path, exist_ok=True)
            snapshot_download(repo_id=_model_name_or_path, local_dir=model_name_or_path)

        self.tokenizer: self.PreTrainedTokenizerFast = (
            self.AutoTokenizer.from_pretrained(model_name_or_path)
        )
        onnx_model_path = os.path.join(model_name_or_path, "grounding_model.onnx")
        self.model: self.onnxruntime.InferenceSession = (
            self.onnxruntime.InferenceSession(onnx_model_path)
        )

    @classmethod
    def default_distilroberta(cls) -> "ORTEmbeddingModel":
        if os.getenv("ORTEmbeddingModelBlobSASURL", None):
            # Just keep old url here
            model_blob_sas_url = os.getenv(
                "ORTEmbeddingModelBlobSASURL",
                "https://dbcopilotshare.blob.core.windows.net/public/grounding-distilroberta-onnx.zip",
            )
            return ORTEmbeddingModel.from_pretrained(model_blob_sas_url)
        else:
            return ORTEmbeddingModel.from_pretrained("linzeqipku/distillroberta.onnx", is_hf=True)

    @classmethod
    @lru_cache(maxsize=16)
    def from_pretrained(cls, model_name_or_path: str, is_hf: bool=False) -> "ORTEmbeddingModel":
        (
            onnxruntime,
            AutoTokenizer,
            PreTrainedTokenizerFast,
            cached_path,
            _,
        ) = dependable_import()
        sw = StopWatcher()
        model = ORTEmbeddingModel(model_name_or_path, is_hf)
        logging.info(
            "ONNXRuntime version = %s, cpu cores = %d, max model length = %d.",
            onnxruntime.__version__,
            multiprocessing.cpu_count(),
            model.tokenizer.model_max_length,
        )
        logging.info(
            "Load Embedding ORT model from `%s` over, cost = %dms",
            model_name_or_path,
            sw.elapsed_ms(),
        )
        return model

    def get_embeddings(
        self,
        texts: List[str],
        batch_size: int = 16,
        verbose: bool = True,
        desc: str = "Get-Embeddings",
        **kwargs,
    ) -> List[np.ndarray]:
        if isinstance(texts, str):
            texts = [texts]

        all_embeddings = []
        for batch_embeddings in self._get_embeddings(texts, batch_size):
            all_embeddings.append(batch_embeddings)

            if verbose and len(all_embeddings) % 100 == 0:
                logging.info(
                    "%s %d/%d ...",
                    desc,
                    len(all_embeddings) * batch_embeddings.shape[0],
                    len(texts),
                )

        all_embeddings = np.concatenate(all_embeddings, 0)
        return all_embeddings

    def _get_embeddings(self, input_texts: List[str], batch_size: int) -> Iterator:
        encoded_inputs = self.tokenizer.batch_encode_plus(input_texts)
        idx = 0
        while idx < len(input_texts):
            batch_encoded_inputs = {
                input_name: encoded_inputs[input_name][idx : idx + batch_size]
                for input_name in encoded_inputs
            }

            embeddings = self.run_model_forward(batch_encoded_inputs)
            yield embeddings

            idx += batch_size

    def run_model_forward(self, enc_inputs: Dict) -> np.ndarray:
        ort_inputs = {
            "input_ids": pad_values_as_numpy(
                enc_inputs["input_ids"],
                self.tokenizer.pad_token_id,
                max_length=self.tokenizer.model_max_length,
            ),
            "attention_mask": pad_values_as_numpy(
                enc_inputs["attention_mask"],
                0,
                max_length=self.tokenizer.model_max_length,
            ),
        }

        output_values = self.model.run(None, input_feed=ort_inputs)
        return output_values[1]
