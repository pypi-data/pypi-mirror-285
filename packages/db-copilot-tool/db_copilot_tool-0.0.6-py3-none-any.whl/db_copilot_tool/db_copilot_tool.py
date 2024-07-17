"""File for the DBCopilot Class."""

import logging
from typing import List

from db_copilot_tool.contracts.db_copilot_config import DBCopilotConfig
from db_copilot_tool.history_service.history_service import HistoryService
from db_copilot_tool.telemetry import enable_appinsights_logging, set_print_logger
from db_copilot_tool.tools.db_copilot_adapter import DBCopilotAdapter
from promptflow import ToolProvider, tool
from promptflow.connections import AzureOpenAIConnection

logging.basicConfig(
    format="[%(asctime)s][%(name)s][%(levelname)s] %(message)s", level=logging.INFO
)


class DBCopilot(ToolProvider):
    """DBCopilot Class."""

    def __init__(
        self,
        embedding_aoai_config: AzureOpenAIConnection,
        chat_aoai_config: AzureOpenAIConnection,
        grounding_embedding_uri: str,
        db_context_uri: str,
        datastore_uri: str,
        embedding_aoai_deployment_name: str,
        chat_aoai_deployment_name: str,
        example_embedding_uri: str = None,
        history_cache_enabled: bool = False,
        history_cache_dir: str = "/tmp/cache",
        selected_tables: List[str] = None,
        max_tables: int = None,
        max_columns: int = None,
        max_rows: int = None,
        max_text_length: int = None,
        max_knowledge_pieces: int = None,
        tools: List[str] = None,
        temperature: float = 0.0,
        top_p: float = 0.0,
        knowledge_pieces: str = None,
        include_views: bool = False,
        instruct_template: str = None,
    ):
        """Initialize the class."""
        set_print_logger()
        enable_appinsights_logging()

        self.config = DBCopilotConfig(
            grounding_embedding_uri=grounding_embedding_uri,
            example_embedding_uri=example_embedding_uri,
            db_context_uri=db_context_uri,
            embedding_aoai_deployment_name=embedding_aoai_deployment_name,
            chat_aoai_deployment_name=chat_aoai_deployment_name,
            datastore_uri=datastore_uri,
            # db_file_name=db_file_name,
            history_cache_enabled=history_cache_enabled,
            history_cache_dir=history_cache_dir,
            selected_tables=selected_tables,
            max_tables=max_tables,
            max_columns=max_columns,
            max_rows=max_rows,
            max_text_length=max_text_length,
            max_knowledge_pieces=max_knowledge_pieces,
            tools=tools,
            temperature=temperature,
            top_p=top_p,
            include_built_in=False,  # prevent from build the sample index which is not supported in the PF container
            knowledge_pieces=knowledge_pieces,
            include_views=include_views,
        )
        logging.info(f"DBCopilot config: {self.config.to_dict()}")
        history_service = HistoryService(self.config.history_service_config)
        self.db_copilot_adaptor = DBCopilotAdapter(
            config=self.config,
            embedding_aoai_connection=embedding_aoai_config,
            chat_aoai_connection=chat_aoai_config,
            history_service=history_service,
            instruct_template=instruct_template,
        )
        super(DBCopilot, self).__init__()

    @tool
    def generate(
        self,
        query: str,
        session_id: str = None,
    ):
        """generate."""
        return self.db_copilot_adaptor.generate(query, session_id)

    def stream_generate(
        self,
        query: str,
        session_id: str = None,
        temperature: float = None,
        top_p: float = None,
    ):
        """stream_generate."""
        return self.db_copilot_adaptor.stream_generate(
            query, session_id, temperature, top_p
        )
