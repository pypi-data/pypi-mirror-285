"""File for the Embedding Service Class."""

import hashlib
import json
import logging
import os
import pathlib
import shutil
from dataclasses import asdict
from typing import Iterator, List

from db_copilot.contract import EmbeddingResult, EmbeddingService
from db_copilot.contract.embedding_core import EmbeddingDocument
from db_copilot_tool.contracts.embedding_config import EmbeddingConfig
from db_copilot_tool.untils.common_index_lookup import CommonIndexLookup
from promptflow.tools.aoai import AzureOpenAI
from promptflow.tools.embedding import embedding
from promptflow_vectordb.tool.faiss_index_lookup import FaissIndexLookup
from promptflow_vectordb.tool.common_index_lookup_utils.constants import (
    IndexTypes,
    QueryTypes,
)


class EmbeddingServiceTool(EmbeddingService):
    def __init__(self, config: EmbeddingConfig):
        """Initialize the class."""
        self.config = config
        self.embedding_search = (
            (
                CommonIndexLookup(
                    index_type=IndexTypes.MLIndexPath,
                    mlindex_path=config.embedding_uri,
                    query_type=QueryTypes.Vector,
                )
                if config.embedding_uri.startswith("azureml://")
                else FaissIndexLookup(config.embedding_uri)
            )
            if config.embedding_uri
            else None
        )
        logging.info(f"embedding_search: {self.embedding_search}")
        self.aoai_provider = AzureOpenAI(config.aoai_connection)

    def build_index(self, docs: Iterator[EmbeddingDocument], **kwargs) -> None:
        if self.config.embedding_uri:
            logging.warning("Index already exists. Skipping build index")
            return
        if self.embedding_search:
            raise Exception("Index already exists")
        # put import here since prompt flow don't depends on rag
        from azureml.rag.documents import StaticDocument
        from db_copilot_tool.tools.embeddings_container_utils import (
            get_embeddings_container,
        )

        def process_docs():
            for doc in docs:
                meta = {
                    "meta": doc.meta,
                    "source": {
                        "filename": hashlib.md5(
                            f"{json.dumps(doc.meta)}-{doc.text}".encode()
                        ).hexdigest()
                    },
                }
                yield StaticDocument(doc.text, meta)

        embeddings_container = get_embeddings_container(self.embed_func)
        embeddings_container = embeddings_container.embed_and_create_new_instance(
            process_docs()
        )
        if self.config.index_cache_folder and os.path.exists(
            self.config.index_cache_folder
        ):
            logging.info(
                f"Removing existing index folder {self.config.index_cache_folder}"
            )
            shutil.rmtree(self.config.index_cache_folder)
        if not os.path.exists(self.config.index_cache_folder):
            os.makedirs(self.config.index_cache_folder)
        logging.info(f"Writing index to {self.config.index_cache_folder}")
        embeddings_container.write_as_faiss_mlindex(
            pathlib.Path(self.config.index_cache_folder)
        )
        self.embedding_search = FaissIndexLookup(self.config.index_cache_folder)
        return

    def search(self, query: str, top_k: int = 5, **kwargs) -> List[EmbeddingResult]:
        assert self.embedding_search is not None
        if isinstance(self.embedding_search, CommonIndexLookup):
            search_results = self.embedding_search.search(query, top_k)
        else:
            vectors = embedding(
                self.config.aoai_connection,
                query,
                deployment_name=self.config.aoai_deployment_name,
            )
            search_results = self.embedding_search.search(vectors, top_k)
        embedding_results = []
        for item in search_results:
            score = item["score"]
            text = item["text"]
            metadata = item["metadata"]
            document = EmbeddingDocument(text=text, meta=metadata.get("meta", metadata))
            embedding_result = EmbeddingResult(score=score, document=document)
            embedding_results.append(embedding_result)
            logging.info(f"embedding_result: {asdict(embedding_result)}")
        return embedding_results

    @property
    def embed_func(self):
        return lambda text: embedding(
            self.config.aoai_connection,
            text,
            deployment_name=self.config.aoai_deployment_name,
        )

    def __del__(self):
        if self.config.index_cache_folder:
            logging.info(f"Removing temp folder: {self.config.index_cache_folder}")
            shutil.rmtree(self.config.index_cache_folder)
