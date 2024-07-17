import hashlib
import json
import os
import pickle
import shutil
import tempfile
from dataclasses import asdict, dataclass
from functools import cached_property
from typing import List, Optional

from azureml.core import Workspace
from db_copilot.db_provider import GroundingConfig, GroundingContext
from db_copilot.db_provider.db_provider_service import DBProviderService
from db_copilot.db_provider.grounding import (
    GroundingConfig,
    GroundingService,
    KnowledgePiece,
)
from db_copilot_tool.contracts.embedding_config import EmbeddingConfig
from db_copilot_tool.history_service.history_service import HistoryService
from db_copilot_tool.tools.db_executor_factory import (
    DBExecutorConfig,
    DBExecutorFactory,
)
from db_copilot_tool.tools.grounding_context_utils import GroundingContextUtils


@dataclass
class DBProviderServiceConfig:
    db_uri: str  # only support long URI
    embedding_service_config: EmbeddingConfig
    grounding_config: GroundingConfig
    db_executor_config: DBExecutorConfig
    knowledge_pieces: Optional[List[KnowledgePiece]] = None
    knowledge_embedding_service_config: Optional[EmbeddingConfig] = None
    history_service: Optional[HistoryService] = None

    def __post_init__(self):
        if not self.grounding_config:
            raise ValueError("grounding_config must be provided")
        if not self.db_executor_config:
            raise ValueError("db_executor_config must be provided")
        if (
            self.knowledge_pieces
            and len(self.knowledge_pieces) > 0
            and not self.knowledge_embedding_service_config
        ):
            raise ValueError(
                "knowledge_embedding_service_config must be provided when knowledge_pieces is provided"
            )
        self.embedding_service = self.embedding_service_config.embedding_service
        if self.knowledge_pieces and self.knowledge_embedding_service_config:
            self.knowledge_embedding_service = (
                self.knowledge_embedding_service_config.embedding_service
            )
            # self.knowledge_service = KnowledgeService(
            #     self.knowledge_pieces, knowledge_embedding_service
            # )
        else:
            self.knowledge_embedding_service = None


class DBProviderServiceAdapter:
    def __init__(
        self,
        config: DBProviderServiceConfig,
        grounding_context: GroundingContext = None,
        history_service: HistoryService = None,
        workspace: Workspace = None,
    ):
        self.config = config
        self.grounding_context_init = grounding_context
        self.history_service = history_service
        self.workspace = workspace
        # trigger grounding
        self.db_provider_service

    @cached_property
    def db_id(self):
        return hashlib.md5(self.config.db_uri.encode("utf-8")).hexdigest()

    @cached_property
    def db_executor(self):
        return DBExecutorFactory.create_executor_with_cache(
            self.config.db_uri,
            self.config.db_executor_config,
            history_service=self.history_service,
            workspace=self.workspace,
        )

    @cached_property
    def grounding_service(self):
        extra_args = {}
        grounding_context_pickle_file: str = None
        if self.grounding_context_init:
            grounding_context_pickle_folder = tempfile.mkdtemp()
            grounding_context_pickle_file = os.path.join(
                grounding_context_pickle_folder, "grounding_context.pkl"
            )
            with open(grounding_context_pickle_file, "wb") as f:
                pickle.dump(self.grounding_context_init, f)
            extra_args["context_pkl_path"] = grounding_context_pickle_file
        if self.config.knowledge_embedding_service:
            extra_args["knowledge_embedding_service"] = (
                self.config.knowledge_embedding_service
            )
        grounding_service = GroundingService.build_from_db_executor(
            self.db_id,
            self.db_executor,
            embedding_service=self.config.embedding_service,
            config=self.config.grounding_config,
            knowledge_pieces=self.config.knowledge_pieces,
            build_index=True,
            **extra_args,
        )
        if grounding_context_pickle_file and os.path.exists(
            grounding_context_pickle_file
        ):
            shutil.rmtree(os.path.dirname(grounding_context_pickle_file))
        return grounding_service

    @cached_property
    def db_provider_service(self):
        return DBProviderService(self.db_executor, self.grounding_service)

    @cached_property
    def retrieve_schema(self):
        return self.db_provider_service.retrieve_schema()

    @property
    def grounding_context(self):
        return self.db_provider_service.grounding_service.context

    @cached_property
    def embedding_service(self):
        return self.db_provider_service.grounding_service.embedding_service

    def dump_context(self, file_folder: str):
        if not os.path.exists(file_folder):
            os.makedirs(file_folder)
        with open(os.path.join(file_folder, "context.pkl"), "wb") as f:
            pickle.dump(self.grounding_context, f)

        for key, value in GroundingContextUtils.to_dict(self.grounding_context).items():
            with open(os.path.join(file_folder, f"{key}.json"), "w") as f:
                json.dump(value, f)

        with open(os.path.join(file_folder, "grounding_config.json"), "w") as f:
            json.dump(asdict(self.config.grounding_config), f)

        with open(os.path.join(file_folder, "db_executor_config.json"), "w") as f:
            json.dump(asdict(self.config.db_executor_config), f)

    @staticmethod
    def load_context(context_folder: str):
        if not os.path.exists(context_folder):
            raise ValueError(f"Folder {context_folder} does not exist.")
        if os.path.exists(os.path.join(context_folder, "context.pickle")):
            context = pickle.load(
                open(os.path.join(context_folder, "context.pickle"), "rb")
            )
            return context
        context_dict = {}
        for file_name in os.listdir(context_folder):
            if file_name.endswith(".json"):
                file = os.path.join(context_folder, file_name)
                value = json.load(open(file, "r"))
                context_dict[file_name.replace(".json", "")] = value
        context = GroundingContextUtils.from_dict(context_dict)
        return context
