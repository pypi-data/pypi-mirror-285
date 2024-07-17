"""File to adapt the DB copilot Agent."""

import json
import logging
import os
import shutil
import tempfile
from dataclasses import asdict
from functools import cached_property

from db_copilot.chat import DefaultDialogueAgent
from db_copilot.contract.llm_core import LLMType
from db_copilot.db_provider import GroundingConfig
from db_copilot.db_provider.grounding import GroundingConfig
from db_copilot.follow_up import FollowUpQueryRewriteSkill
from db_copilot.llm import OpenaiChatLLM
from db_copilot.planner import DefaultPlanner
from db_copilot.suggestion import SuggestionGenerationSkill
from db_copilot.tool import PythonExecuteTool, SQLExecuteTool
from db_copilot_tool.contracts.db_copilot_config import DBCopilotConfig
from db_copilot_tool.contracts.embedding_config import EmbeddingConfig
from db_copilot_tool.history_service.dialogue_sessions import DialogueSession
from db_copilot_tool.history_service.history_service import HistoryService
from db_copilot_tool.telemetry import get_logger, track_activity, track_function
from db_copilot_tool.tools.azureml_asset_handler import DatastoreDownloader
from db_copilot_tool.tools.db_executor_factory import DBExecutorConfig
from db_copilot_tool.tools.db_provider_adapter import (
    DBProviderServiceAdapter,
    DBProviderServiceConfig,
)
from db_copilot_tool.tools.in_context_learning_agent import InContextLearningAgent
from db_copilot_tool.tools.json_handler import convert_to_json_serializable
from promptflow.connections import AzureOpenAIConnection


class DBCopilotAdapter:
    @track_function(name="DBCopilotAdapter:init")
    def __init__(
        self,
        config: DBCopilotConfig,
        embedding_aoai_connection: AzureOpenAIConnection,
        chat_aoai_connection: AzureOpenAIConnection,
        history_service: HistoryService = None,
        cache_folder: str = None,
        instruct_template: str = None,
    ):
        self.chat_aoai_connection = chat_aoai_connection
        self.history_service = history_service
        self.embedding_aoai_connection = embedding_aoai_connection
        self.config = config
        self.cache_folder = cache_folder if cache_folder else tempfile.mkdtemp()
        self.instruct_template = None if instruct_template == "" else instruct_template
        if not os.path.exists(self.cache_folder):
            os.makedirs(self.cache_folder)
        self.temp_folder = self.cache_folder if not cache_folder else None
        with open(self.config_file, "w") as f:
            json.dump(asdict(self.config), f)
        # trigger grounding
        self.dialogue_agent

    @cached_property
    def config_file(self):
        return os.path.join(self.cache_folder, "config.json")

    @cached_property
    def db_executor_config(self):
        db_executor_config = DBExecutorConfig()
        if self.config.selected_tables:
            db_executor_config.tables = self.config.selected_tables
        if self.config.column_settings:
            db_executor_config.column_settings = self.config.column_settings
        if self.config.include_views:
            if db_executor_config.metadata is None:
                db_executor_config.metadata = {}
            db_executor_config.metadata["include_views"] = self.config.include_views
        return db_executor_config

    @cached_property
    def grounding_config(self):
        grounding_config = GroundingConfig()
        if self.config.max_tables:
            grounding_config.max_tables = self.config.max_tables
        if self.config.max_columns:
            grounding_config.max_columns = self.config.max_columns
        if self.config.max_rows:
            grounding_config.max_rows = self.config.max_rows
        if self.config.max_sampling_rows:
            grounding_config.max_sampling_rows = self.config.max_sampling_rows
        if self.config.max_text_length:
            grounding_config.max_text_length = self.config.max_text_length
        if self.config.max_knowledge_pieces:
            grounding_config.max_knowledge_pieces = self.config.max_knowledge_pieces
        return grounding_config

    @cached_property
    def chat_llm(self):
        return OpenaiChatLLM(
            llm_type=LLMType.GPT35_TURBO,
            api_base=self.chat_aoai_connection.api_base,
            api_key=self.chat_aoai_connection.api_key,
            api_version=self.chat_aoai_connection.api_version,
            api_type=self.chat_aoai_connection.api_type,
            model=self.config.chat_aoai_deployment_name,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
        )

    @cached_property
    def grounding_embedding_cache_folder(self):
        return os.path.join(self.cache_folder, "grounding_embedding_cache")

    @cached_property
    def grounding_embedding_service_config(self):
        return EmbeddingConfig(
            embedding_uri=(
                self.config.grounding_embedding_uri
                if self.config.grounding_embedding_uri
                else (
                    self.grounding_embedding_cache_folder
                    if os.path.exists(self.grounding_embedding_cache_folder)
                    else None
                )
            ),
            index_cache_folder=(
                None
                if self.config.grounding_embedding_uri
                else self.grounding_embedding_cache_folder
            ),
            aoai_deployment_name=self.config.embedding_aoai_deployment_name,
            aoai_connection=self.embedding_aoai_connection,
        )

    @cached_property
    def example_embedding_cache_folder(self):
        return os.path.join(self.cache_folder, "example_embedding_cache")

    @cached_property
    def example_embedding_service_config(self):
        return EmbeddingConfig(
            embedding_uri=(
                self.config.example_embedding_uri
                if self.config.example_embedding_uri
                else (
                    self.example_embedding_cache_folder
                    if os.path.exists(self.example_embedding_cache_folder)
                    else None
                )
            ),
            index_cache_folder=(
                None
                if self.config.example_embedding_uri
                else self.example_embedding_cache_folder
            ),
            aoai_deployment_name=self.config.embedding_aoai_deployment_name,
            aoai_connection=self.embedding_aoai_connection,
        )

    @cached_property
    def examples(self):
        return InContextLearningAgent.get_examples(
            example_uri=self.config.example_uri,
            db_type=self.db_provider_service.db_type,
            tools=self.tools,
            include_built_in=self.config.include_built_in,
        )

    @cached_property
    def in_context_learning_agent(self):
        if (
            self.examples is None or len(self.examples) == 0
        ) and not self.config.example_embedding_uri:
            logging.info("No examples found, skip in-context learning")
            return None
        return InContextLearningAgent(
            embedding_config=self.example_embedding_service_config,
            examples=self.examples,
        )

    @cached_property
    def knownledge_embedding_cache_folder(self):
        return os.path.join(self.cache_folder, "knowledge_index_cache")

    @cached_property
    def knownledge_embedding_service_config(self):
        return EmbeddingConfig(
            embedding_uri=(
                self.knownledge_embedding_cache_folder
                if os.path.exists(self.knownledge_embedding_cache_folder)
                else None
            ),
            index_cache_folder=self.knownledge_embedding_cache_folder,
            aoai_deployment_name=self.config.embedding_aoai_deployment_name,
            aoai_connection=self.embedding_aoai_connection,
        )

    @cached_property
    def grounding_context(self):
        if self.config.db_context_uri:
            if self.config.db_context_uri.startswith("azureml://"):
                with DatastoreDownloader(
                    self.config.db_context_uri
                ) as db_context_folder:
                    return DBProviderServiceAdapter.load_context(db_context_folder)
            else:
                return DBProviderServiceAdapter.load_context(self.config.db_context_uri)
        return None

    @cached_property
    def db_provider_service(self):
        db_provider_config = DBProviderServiceConfig(
            db_uri=self.config.datastore_uri,
            embedding_service_config=self.grounding_embedding_service_config,
            grounding_config=self.grounding_config,
            db_executor_config=self.db_executor_config,
            knowledge_pieces=self.config.knowledge_pieces,
            knowledge_embedding_service_config=self.knownledge_embedding_service_config,
        )

        db_provider_service_adapter = DBProviderServiceAdapter(
            db_provider_config, self.grounding_context, self.history_service
        )
        # cache context if not exist
        if not self.grounding_context:
            db_provider_service_adapter.dump_context(
                os.path.join(self.cache_folder, "db_context")
            )
        return db_provider_service_adapter.db_provider_service

    @cached_property
    def grounding_service(self):
        self.db_provider_service.grounding_service

    @cached_property
    def db_executor(self):
        return self.db_provider_service.db_executor

    @cached_property
    def tools(self):
        tools_obj = {}
        sql_tool = SQLExecuteTool(self.db_provider_service)
        tools_obj[self.db_provider_service.sql_dialect.value] = sql_tool
        if self.config.tools != None and "python" in self.config.tools:
            python_tool = PythonExecuteTool()
            tools_obj["python"] = python_tool
        return tools_obj

    @cached_property
    def planner(self):
        return DefaultPlanner(tool_dict=self.tools, llm=self.chat_llm)

    @cached_property
    def follow_up_skill(self):
        return FollowUpQueryRewriteSkill(self.chat_llm)

    @cached_property
    def suggestion_generation_skill(self):
        return SuggestionGenerationSkill(self.chat_llm)

    @cached_property
    def dialogue_agent(self):
        return DefaultDialogueAgent(
            db_provider_agent=self.db_provider_service,
            in_context_learning_agent=self.in_context_learning_agent,
            planner=self.planner,
            follow_up_skill=self.follow_up_skill,
            suggestion_skill=self.suggestion_generation_skill,
            instruct_template=self.instruct_template,
        )

    def get_memory(self, session_id: str):
        if session_id and self.history_service and self.history_service.enabled:
            session = self.history_service.get_dialogue_session(session_id)
        else:
            session = DialogueSession()
        memory = session.messageHistory
        logging.info(
            f"Get Recent Memory. session id: {session_id}, cache dir: {os.path.abspath(self.config.history_service_config.cache_dir)}. memory: {memory}"
        )
        return session, memory

    def stream_generate(
        self,
        query: str,
        session_id: str = None,
        temperature: float = None,
        top_p: float = None,
        extra_kwargs: dict = {},
    ):
        logger = get_logger("db_copilot_tool")
        with track_activity(logger, "db_copilot_tool.generate") as activity_logger:
            session, memory = self.get_memory(session_id)
            stream_response_count = 0
            response_count = 0
            if not extra_kwargs:
                extra_kwargs = {}
            for response in self.dialogue_agent.interact(
                query, memory, temperature=temperature, top_p=top_p, **extra_kwargs
            ):
                new_memory = response.memory
                if new_memory:
                    session.messageHistory = new_memory
                    if (
                        session_id
                        and self.history_service
                        and self.history_service.enabled
                    ):
                        self.history_service.set_dialogue_session(session_id, session)
                stream_response_count = len(response.cells)
                yield [
                    convert_to_json_serializable(asdict(cell))
                    for cell in response.cells
                ]
            activity_logger.activity_info["stream_response_count"] = (
                stream_response_count
            )
            activity_logger.activity_info["response_count"] = response_count

    def generate(
        self,
        query: str,
        session_id: str = None,
        temperature: float = None,
        top_p: float = None,
        extra_kwargs: dict = {},
    ):
        """generate."""
        response = list(
            self.stream_generate(
                query=query,
                session_id=session_id,
                temperature=temperature,
                top_p=top_p,
                extra_kwargs=extra_kwargs,
            )
        )[-1]
        logging.info(f"response: {response}")
        return response

    def get_example_queries(self, query: str, session_id: str = None):
        logger = get_logger("db_copilot_tool")
        with track_activity(
            logger, "db_copilot_tool.get_example_queries"
        ) as activity_logger:
            _, memory = self.get_memory(session_id)
            return self.dialogue_agent.suggest(query, memory)

    @cached_property
    def summary(self):
        logger = get_logger("db_copilot_tool")
        with track_activity(logger, "db_copilot_tool.get_summary") as activity_logger:
            schemas = self.db_provider_service.retrieve_schema()
            schemas_as_string = schemas.as_prompt_text(
                max_tables=self.config.max_tables
            )
            schemas_as_dict = schemas.to_dict()
            completion = (
                "This database contains the following tables:\n```data\n"
                + schemas_as_string
                + "\n```"
            )
            return completion, schemas_as_dict

    def __del__(self):
        if self.temp_folder and os.path.exists(self.temp_folder):
            shutil.rmtree(self.temp_folder)
