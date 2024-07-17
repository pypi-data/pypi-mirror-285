import csv
import os
from dataclasses import dataclass
from typing import Dict, List

from db_copilot.contract import DictMixin, KnowledgePiece

from .grounding import GroundingConfig


@dataclass
class DBProviderConfig(DictMixin):
    """
    Config for a db provider service.
    Args:
        db_id (`str`, *required*):
            Unique id to access db provider service
        conn_string (`str`, *required*):
            A string value to connect to the database. The connect string must starts with the database type.
            For example, `sqlite://https://**/**/sample.sqlite`, `sqlserver://{{odbc_conn_string}};`.
        grounding_config (`GroundingConfig`, *optional*, defaults to `None`):
            Grounding settings. `None` will create a default `GroundingConfig` instance.
        selected_tables (`List[str]`, *optional*, defaults to `None`):
            User defined tables for the service. Default `None` will use all queried tables.
            Table name is case-sensitive.
        column_settings (`List[Dict[str, object]]`, *optional*, defaults to `None`):
            User defined settings for table/columns, such as security_level, description.
            Defaults to `None` which means no specific settings.
            The key is full name of the column which equals to `{table_name}.{column_name}`.
        metadata (`Dict[str, object]`, *optional*, defaults to `None`):
            Metadata to store dynamic values, which may be required to service building.
            For example, `db_bytes` to bytes of a database (only used for sqlite).
    """
    db_id: str
    conn_string: str = None
    grounding_config: GroundingConfig = None
    selected_tables: List[str] = None
    column_settings: List[Dict] = None
    knowledge_pieces: List[KnowledgePiece] = None
    metadata: Dict[str, object] = None

    @classmethod
    def from_dict(cls, obj: Dict) -> "DBProviderConfig":
        if 'column_settings' not in obj:
            if 'schema_settings' in obj:
                obj["column_settings"] = obj.pop("schema_settings")

        if 'grounding_config' in obj:
            obj["grounding_config"] = GroundingConfig.from_dict(obj["grounding_config"])

        if obj.get('knowledge_pieces', None):
            obj['knowledge_pieces'] = [KnowledgePiece.from_dict(x) for x in obj["knowledge_pieces"]]

        if obj.get('knowledge_pieces_for_values', None):
            # the value description will be csv file, so process each row of the csv into knowledge pieces in the obj['knowledge_pieces']
            for value_description in obj.pop('knowledge_pieces_for_values'):
                obj['knowledge_pieces'].extend(
                    DBProviderConfig.process_knowledge_pieces_from_csv(
                        value_description.get('db_name', None), 
                        value_description.get('table_name', None), 
                        value_description.get('column_name', None), 
                        value_description.get('value_column', 'value'),
                        value_description.get('description_columnn', 'description'),
                        value_description.get('files', None)))

        metadata = obj.pop("metadata", {})
        for key in list(obj.keys()):
            if key not in { "db_id", "conn_string", "grounding_config", "selected_tables", "column_settings", "knowledge_pieces" }:
                metadata[key] = obj.pop(key)
        obj["metadata"] = metadata
        return cls(**obj)

    def get_value(self, value: str) -> object:
        """
        Get actual value defined in this config 
        """
        # environment value
        if value.startswith("{{") and value.endswith("}}"):
            return os.getenv(value[2:-2])

        # metadata value
        if value.startswith("<<") and value.endswith(">>"):
            assert self.metadata is not None, f"Field `metadata` is require as we detect a metadata value `{value}`."
            return self.metadata.get(value[2:-2])
        
        return value
    
    @staticmethod
    def process_knowledge_pieces_from_csv(db_name : str, table_name : str, column_name : str, value_column : str, description_column : str, paths : List[str]) -> List[KnowledgePiece]:
        if db_name is None or table_name is None or column_name is None or paths is None:
            raise ValueError("Missing parameters: db_name, table_name, column_name, or paths")

        knowledge_pieces = []
        source = f'{db_name.strip()}.{table_name.strip()}.{column_name.strip()}'
        for path in paths:
            with open(path, 'r') as csv_file:
                # Create a CSV reader object
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    # Process each row as needed
                    value = row.get(value_column).strip()
                    description = row.get(description_column).strip()
                    entity = f'{source}.{value}'

                    # construct to knowledge piece
                    if value and description:
                        temp = {}
                        temp['text'] = description
                        temp['entities'] = [entity]
                        temp['prompt_text'] = f"The meaning of {entity} is {description}"
                        knowledge_pieces.append(KnowledgePiece.from_dict(temp))
        return knowledge_pieces

