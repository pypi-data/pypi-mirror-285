from dataclasses import dataclass
from typing import Union, List, Dict, Any
from enum import Enum
from collections import defaultdict
from functools import cached_property
import logging

from db_copilot.contract import ColumnSchema, TableSchema, TableData, ColumnSecurityLevel, EmbeddingDocument
from db_copilot.db_provider.db_executor import DBExecutor, DatabaseType, DataTypeCategory
from db_copilot.db_provider.utils import string_utils

class ConceptType(str, Enum):
    """
    Pre-defined concept types
    """
    CONSTANT = "constant"
    FUNCTION = "function"
    ENTITY = "entity"
    TABLE = "table"
    COLUMN = "column"
    VALUE = "value"
    USER_DEFINED = "user_defined"
    
    def __str__(self) -> str:
        return self.value


@dataclass
class DBConcept:
    id: Union[int, str]
    type: ConceptType
    name: str
    parent: Union[int, str] = None
    description: str = None
    schema: Union[TableSchema, ColumnSchema, int] = None # Corresponding schema info. For `value`, it refers to the row index.

    def to_document(self, **kwargs) -> EmbeddingDocument:
        metadata = {
            'id': self.id,
            'type': self.type.value,
            'parent': self.parent
        }

        encoding_text = self.name
        if kwargs.get("encode_dependency", False):
            context: GroundingContext = kwargs.get("context", None)
            assert context is not None, 'context is required to encode dependency'
            parents = context.lookup_parent_concepts(self.id, reverse=True)
            parent_names = [c.name for c in parents]
            encoding_text = "{} {}".format(" ".join(parent_names), encoding_text)

        if kwargs.get("encode_description", True) and self.description:
            encoding_text += f": {self.description}"

        return EmbeddingDocument(
            text=encoding_text,
            meta=metadata
        )

class GroundingContext:
    context_id: str
    db_type: DatabaseType
    def __init__(self, context_id: str, db_type: DatabaseType, concepts: List[DBConcept], table_schemas: Dict[str, TableSchema], sample_data: Dict[str, TableData]) -> None:
        self.context_id = context_id
        self.db_type = db_type
        self._concepts = concepts

        self.table_schemas = table_schemas

        # Sampled tabular data for each table
        self.sample_data = sample_data

    @property
    def concepts(self) -> List[DBConcept]:
        # TODO: optimize when the number of concepts is too large.
        return self._concepts

    @cached_property
    def entity_to_concepts(self) -> Dict[str, int]:
        entity_to_concepts = {}
        for concept in self.concepts:
            concepts = self.lookup_parent_concepts(concept, reverse=True) + [concept]
            full_name = ".".join([c.name for c in concepts])
            entity_to_concepts[full_name] = concept.id

        return entity_to_concepts

    def __len__(self) -> int:
        return len(self._concepts)
    
    def get_table_to_columns(self) -> Dict[int, List[int]]:
        table2columns = defaultdict(list)
        for concept in self.concepts:
            if concept.type == ConceptType.COLUMN:
                table2columns[concept.parent].append(concept.id)
        return table2columns

    def lookup_concept(self, concept_id: Union[int, str]) -> DBConcept:
        assert isinstance(concept_id, int)
        return self.concepts[concept_id]

    def lookup_parent_concepts(self, concept: Union[int, str, DBConcept], reverse: bool=False) -> List[DBConcept]:
        if isinstance(concept, (int, str)):
            concept_id = concept
            concept = self.lookup_concept(concept_id)
            assert concept is not None, "Concept not found by id `{}`".format(concept_id)
        
        parents = []
        parent_id = concept.parent
        while parent_id >= 0:
            parent_concept = self.lookup_concept(parent_id)
            parents.append(parent_concept)
            parent_id = parent_concept.parent
        
        if reverse:
            return parents[::-1]

        return parents

    @classmethod
    def from_db_executor(cls, db_id: str, db_executor: DBExecutor, max_sampling_rows: int, max_text_length: int) -> "GroundingContext":
        """
        Build context from database
        """
        concepts: List[DBConcept] = []
        def _add_concept(c_type: ConceptType, name: str, parent: int=-1, schema: Any=None, desc: str=None) -> int:
            concept = DBConcept(
                id=len(concepts),
                type=c_type,
                name=name,
                parent=parent,
                schema=schema,
                description=desc
            )
            concepts.append(concept)
            return concept.id

        sample_data: Dict[str, TableData] = db_executor.sample_rows(max_sampling_rows)

        total_sampling_values = 0
        for tbl_name, tbl_schema in db_executor.table_schemas.items():
            tbl_concept_id = _add_concept(ConceptType.TABLE, tbl_name, parent=-1, schema=tbl_schema, desc=tbl_schema.description)

            tbl_sample_data: TableData = sample_data.get(tbl_name, None)
            for c_idx, col_schema in enumerate(tbl_schema.columns):
                col_concept_id = _add_concept(
                    ConceptType.COLUMN, name=col_schema.name,
                    parent=tbl_concept_id, schema=col_schema, desc=col_schema.description
                )

                if not tbl_sample_data or col_schema.security_level > ColumnSecurityLevel.NORMAL:
                    continue

                data_type_category = DataTypeCategory.from_data_type(col_schema.data_type, db_executor.db_type)
                if data_type_category != DataTypeCategory.Text:
                    continue

                distinct_values = set([])
                for r_idx in range(len(tbl_sample_data.data)):
                    c_value = tbl_sample_data.data[r_idx][c_idx]
                    if c_value is None or not isinstance(c_value, str) or len(c_value) > max_text_length:
                            continue

                    c_value_norm = c_value.strip().lower()
                    if not c_value_norm:
                        continue
                    
                    if string_utils.is_general_number(c_value.strip()) or string_utils.is_uuid(c_value.strip()) or string_utils.is_ip_address(c_value.strip()):
                        continue

                    if c_value_norm in distinct_values:
                        continue

                    _ = _add_concept(ConceptType.VALUE, name=str(c_value), parent=col_concept_id, schema=r_idx)
                    total_sampling_values += 1
                    distinct_values.add(c_value_norm)
        
        logging.info("Database `%s` sample %d/%d concepts for grounding over.", db_id, len(concepts), total_sampling_values)
        return GroundingContext(db_id, db_executor.db_type, concepts, db_executor.table_schemas, sample_data)
