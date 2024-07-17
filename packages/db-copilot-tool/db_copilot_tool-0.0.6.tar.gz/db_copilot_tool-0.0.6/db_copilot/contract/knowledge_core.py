from dataclasses import dataclass
from typing import List, Dict

from .generic import PromptMixin, DictMixin, get_field_names


@dataclass
class KnowledgePiece(DictMixin, PromptMixin):
    type: str = 'document'
    priority: int = 3
    entities: List[str] = None
    metadata: Dict[str, object] = None

    @staticmethod
    def all_knowledge_classes() -> Dict:
        # builtin knowledge classes
        knowledge_classes =  {
            'metadata': Metadata,
            'concept': Concept,
            'formula': Formula,
            'document': Document
        }
        
        return knowledge_classes

    @classmethod
    def from_dict(cls, obj: dict) -> "KnowledgePiece":
        knowledge_type = obj.pop("type", 'document')
        knowledge_classes = cls.all_knowledge_classes()
        type_cls = knowledge_classes.get(knowledge_type, Document)
        return type_cls.from_dict(obj)

    def get_value_from_fields(self, fields: List[str]):
        for field in fields:
            if not field:
                continue
            if self.metadata.get(field, None):
                return self.metadata[field]
            if getattr(self, field, None):
                return getattr(self, field)
        return None

    def get_embedding_text(self, **kwargs) -> str:
        return self.get_value_from_fields(
            [kwargs.get("field_key", None)] + ["embedding_text", "text"]
        )

    def as_prompt_text(self, **kwargs) -> str:
        return self.get_value_from_fields(
            [kwargs.get("field_key", None)] + ["prompt_text", "text"]
        )


@dataclass
class KnowledgeImp(KnowledgePiece):
    @classmethod
    def from_dict(cls, obj: dict) -> "KnowledgeImp":
        fields = get_field_names(cls)
        metadata = obj.get("metadata", {})
        for field_name in list(obj.keys()):
            if field_name not in fields:
                metadata[field_name] = obj.pop(field_name)
        obj["metadata"] = metadata
        return cls(**obj)

    @property
    def default_text(self):
        raise NotImplementedError()

    def get_embedding_text(self, **kwargs) -> str:
        embedding_text = super().get_embedding_text(**kwargs)
        return embedding_text if embedding_text else self.default_text

    def as_prompt_text(self, **kwargs) -> str:
        prompt_text = super().as_prompt_text(**kwargs)
        return prompt_text if prompt_text else self.default_text

@dataclass
class Metadata(KnowledgeImp):
    type = "metadata"
    entity: str = None # name of entity, should be table name, column full name(with table name)
    description: str = None

    def  __post_init__(self):
        assert self.entity is not None, "entity name is required to create Entity Metadata Knowledge piece"

    @property
    def default_text(self):
        return "{}: {}".format(self.entity, self.description)


@dataclass
class Concept(KnowledgeImp):
    type = "concept"
    concept: str = None
    definition: str = None

    def __post_init__(self):
        assert self.concept is not None
        assert self.definition is not None
        self.concept = self.concept.strip().replace('\n', " ")
        self.definition = self.definition.strip().replace("\n", " ")
    
    @property
    def default_text(self):
        return "{}: {}".format(self.concept, self.definition)


@dataclass
class Formula(KnowledgeImp):
    type = "formula"
    expression: str = None

    @property
    def default_text(self):
        return self.expression


@dataclass
class Document(KnowledgeImp):
    type = "document"
    text: str = None

    def __post_init__(self):
        if self.text is None:
            embedding_text = self.get_embedding_text()
            prompt_text = self.as_prompt_text()
            assert embedding_text is not None or prompt_text is not None, "invalid document: `text` or (`embedding_text`/`prompt_text`) is required."
