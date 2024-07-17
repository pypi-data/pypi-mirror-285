from dataclasses import asdict

from db_copilot.contract.db_core import (
    ColumnSchema,
    DatabaseType,
    TableData,
    TableSchema,
)
from db_copilot.db_provider import ConceptType, DBConcept, GroundingContext
from db_copilot.db_provider.db_executor import DatabaseType
from db_copilot.db_provider.grounding.grounding_service import GroundingContext


class GroundingContextUtils:
    @staticmethod
    def to_dict(context: GroundingContext):
        result = {}
        result["concepts"] = [asdict(concept) for concept in context.concepts]
        result["table_schemas"] = {
            name: schema.to_dict() for name, schema in context.table_schemas.items()
        }
        result["sample_data"] = {
            name: sample.to_dict() for name, sample in context.sample_data.items()
        }
        result["db_type"] = context.db_type.value
        result["context_id"] = context.context_id
        return result

    @staticmethod
    def from_dict(context_dict: dict):
        concepts = []
        for concept in context_dict["concepts"]:
            dbconcept = DBConcept(**concept)
            dbconcept.type = ConceptType(dbconcept.type)
            if dbconcept.type == ConceptType.TABLE:
                dbconcept.schema = TableSchema.from_dict(dbconcept.schema)
            elif dbconcept.type == ConceptType.COLUMN:
                dbconcept.schema = ColumnSchema.from_dict(dbconcept.schema)
            concepts.append(dbconcept)
        table_schemas = {}
        for table_name, schema in context_dict["table_schemas"].items():
            table_schemas[table_name] = TableSchema.from_dict(schema)
        sample_data = {}
        for table_name, table_data in context_dict["sample_data"].items():
            sample_data[table_name] = TableData.from_dict(table_data)
        if "db_type" in context_dict:
            db_type = DatabaseType(context_dict["db_type"])
        else:
            db_type = DatabaseType.SQLSERVER
        if "context_id" in context_dict:
            context_id = context_dict["context_id"]
        else:
            context_id = "default_context"
        return GroundingContext(
            context_id, db_type, concepts, table_schemas, sample_data
        )
