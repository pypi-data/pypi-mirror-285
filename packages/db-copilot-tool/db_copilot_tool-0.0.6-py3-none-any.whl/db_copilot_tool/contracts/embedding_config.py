import logging
import os
from dataclasses import dataclass
from functools import cached_property

from db_copilot_tool.tools.dummy_embedding_service import DummyEmbeddingService
from promptflow.connections import AzureOpenAIConnection


@dataclass
class EmbeddingConfig:
    """EmbeddingConfig Class."""

    aoai_deployment_name: str = None
    embedding_uri: str = None
    index_cache_folder: str = None
    aoai_connection: AzureOpenAIConnection = None

    def __post_init__(self):
        if self.aoai_connection and bool(self.embedding_uri) == bool(
            self.index_cache_folder
        ):
            if self.embedding_uri and self.embedding_uri != self.index_cache_folder:
                raise ValueError(
                    f"Either embedding_uri({self.embedding_uri}) or embedding_folder({self.index_cache_folder}) should be provided."
                )
        if (
            self.index_cache_folder
            and os.path.exists(self.index_cache_folder)
            and len(os.listdir(self.index_cache_folder)) > 0
        ):
            logging.warning(f"Index folder {self.index_cache_folder} is not empty.")

        if self.aoai_connection and not self.aoai_deployment_name:
            raise ValueError(
                "aoai_deployment_name must be provided when aoai_connection is provided."
            )

    @cached_property
    def embedding_service(self):
        from db_copilot_tool.tools.embedding_service import EmbeddingServiceTool

        if self.aoai_connection:
            return EmbeddingServiceTool(self)
        else:
            return DummyEmbeddingService()
