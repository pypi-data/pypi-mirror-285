"""Config File for DB Copilot Tool Contracts."""

import json
from dataclasses import asdict, dataclass
from typing import Dict, List, Union

from db_copilot.db_provider.grounding import GroundingConfig, KnowledgePiece
from db_copilot_tool.history_service.history_service import HistoryServiceConfig


@dataclass
class DBCopilotConfig:
    """DBCopilotConfig Class."""

    datastore_uri: str
    embedding_aoai_deployment_name: str
    chat_aoai_deployment_name: str
    grounding_embedding_uri: str = None
    example_embedding_uri: str = None
    db_context_uri: str = None
    selected_tables: Union[str, List[str]] = None
    max_tables: int = None
    max_columns: int = None
    max_rows: int = None
    max_text_length: int = None
    max_knowledge_pieces: int = None
    history_cache_enabled: bool = False
    history_cache_dir: str = "/tmp/cache"
    tools: Union[str, List[str]] = None
    temperature: float = 0.0
    top_p: float = 0.0
    # promptflow exclusive propertys
    knowledge_pieces: Union[str, List[dict], List[KnowledgePiece]] = None
    example_uri: str = None
    max_sampling_rows: int = None
    column_settings: Union[str, Dict[str, Dict[str, str]]] = None
    include_built_in: bool = True
    include_views: bool = False

    def __post_init__(self):
        if self.selected_tables and isinstance(self.selected_tables, str):
            self.selected_tables = json.loads(self.selected_tables)
            if not isinstance(self.selected_tables, list):
                raise ValueError("selected_tables must be a list")
        if self.tools and isinstance(self.tools, str):
            self.tools = json.loads(self.tools)
            if not isinstance(self.tools, list):
                raise ValueError("tools must be a dict")
        if self.knowledge_pieces:
            if isinstance(self.knowledge_pieces, str):
                self.knowledge_pieces = json.loads(self.knowledge_pieces)
            if not isinstance(self.knowledge_pieces, list):
                raise ValueError("knowledge_pieces must be a list")
            self.knowledge_pieces = [
                (
                    KnowledgePiece.from_dict(knowledge_piece)
                    if isinstance(knowledge_piece, dict)
                    else knowledge_piece
                )
                for knowledge_piece in self.knowledge_pieces
            ]

    def to_dict(self) -> Dict[str, Union[None, str, bool, int, float]]:
        return asdict(self)

    def to_db_copilot_dict(self):
        config_dict = self.to_dict()
        for key in [
            "knowledge_pieces",
            "example_uri",
            "max_sampling_rows",
            "column_settings",
            "include_built_in",
        ]:
            config_dict.pop(key, None)
        return config_dict

    @property
    def history_service_config(self) -> HistoryServiceConfig:
        """Return HistoryServiceConfig."""
        return HistoryServiceConfig(
            history_service_enabled=self.history_cache_enabled,
            cache_dir=self.history_cache_dir,
            expire_seconds=3600,
            max_cache_size_mb=100,
        )

    @property
    def grounding_config(self) -> GroundingConfig:
        grounding_config = GroundingConfig()
        if self.max_tables:
            grounding_config.max_tables = self.max_tables
        if self.max_columns:
            grounding_config.max_columns = self.max_columns
        if self.max_rows:
            grounding_config.max_rows = self.max_rows
        if self.max_text_length:
            grounding_config.max_text_length = self.max_text_length
        if self.max_knowledge_pieces:
            grounding_config.max_knowledge_pieces = self.max_knowledge_pieces
        return grounding_config
