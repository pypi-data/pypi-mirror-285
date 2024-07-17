"""
Basic interface definition
"""
import abc
from dataclasses import fields, dataclass
from typing import AbstractSet
import json
from enum import Enum


def convert_object_to_dict(obj):
    """
    Convert a python object to json object
    """
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()

    if isinstance(obj, (list, tuple)):
        return [convert_object_to_dict(x) for x in obj]

    if isinstance(obj, dict):
        return { k : convert_object_to_dict(v) for k, v in obj.items() }

    if isinstance(obj, Enum):
        return obj.value

    return obj


def get_field_names(cls):
    """
    Get all field names of a data class
    """
    class_fields = fields(cls)
    return { f.name for f in class_fields }


@dataclass
class DictMixin:
    """
    Base class for JSON-serializable classes
    """

    @property
    def fields(self) -> AbstractSet:
        """
        Fields names
        """
        cls_fields = fields(self)
        return {f.name for f in cls_fields }

    def __hash__(self) -> int:
        return self.to_tuple().__hash__()

    def __eq__(self, other: object) -> bool:
        if other is None:
            return False

        if not isinstance(other, DictMixin):
            return False

        field_names = self.fields
        other_field_names = other.fields

        if field_names != other_field_names:
            return False

        return all([self[field_name] == other[field_name] for field_name in field_names])

    def __delitem__(self, *args, **kwargs):
        raise IndexError(f"You cannot use ``__delitem__`` on a {self.__class__.__name__} instance.")

    def __getitem__(self, key):
        if key not in self.fields:
            raise KeyError(f"``{key}`` not found on a {self.__class__.__name__} instance.")
        return getattr(self, key)

    @classmethod
    def from_dict(cls, obj: dict) -> "DictMixin":
        """
        Deserialize the class instance from a json object
        """
        field_names = get_field_names(cls)
        return cls(**{k : v for k, v in obj.items() if k in field_names})

    def to_tuple(self) -> tuple:
        """
        Convert the dataclass into a tuple
        """
        return [self[x] for x in self.fields]

    @classmethod
    def from_json(cls, json_string: str) -> "DictMixin":
        """
        Deserialize the class instance from a json string
        """
        obj = json.loads(json_string)
        return cls.from_dict(obj)

    def to_dict(self) -> dict:
        """
        Serialize the instance into a json object
        """
        return { k : convert_object_to_dict(self[k]) for k in self.fields }

    def to_json(self) -> str:
        """
        Serialize the instance into a json string
        """
        obj = self.to_dict()
        return json.dumps(obj)


@dataclass
class PromptMixin:
    """
    Data class definition with `as_prompt_text` method
    """
    @abc.abstractmethod
    def as_prompt_text(self, **kwargs) -> str:
        """
        Convert the data classes into text for prompt construction
        """


class TaskStatusCode(int, Enum):
    """
    Status code enum definition
    """
    COMPLETED = 0
    FAILED = 1
    RUNNING = 2
    PENDING = 3
    CANCEL = 4
