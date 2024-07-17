from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum

from .generic import DictMixin
from .tool_core import CodeInfo

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message(DictMixin):
    role: MessageRole
    content: str
    
    def to_message(self) -> str:
        return f"{self.role.value}: {self.content}\n"
    
    @classmethod
    def from_dict(cls, obj: dict) -> "Message":
        obj["role"] = MessageRole(obj["role"])
        return super().from_dict(obj)


@dataclass
class MemoryItem(DictMixin):
    role: MessageRole
    content: str
    code_infos: Optional[List[CodeInfo]]

    @classmethod
    def from_dict(cls, obj: Dict) -> "MemoryItem":
        obj["role"] = MessageRole(obj["role"])
        code_lst = obj.get("code_infos", None)
        if code_lst and isinstance(code_lst, list):
            obj["code_infos"] = [CodeInfo.from_dict(x) for x in code_lst]

        return super().from_dict(obj)

@dataclass
class MemoryManager(ABC):
    @abstractmethod
    def init(self, items: List[MemoryItem]):
        pass

    @abstractmethod
    def add(self, item: MemoryItem):
        pass

    @abstractmethod
    def retrieve(self, query: str) -> List[MemoryItem]:
        pass

    @abstractmethod
    def get_memory(self) -> List[MemoryItem]:
        pass
    
    @abstractmethod
    def generate_unique_code_id(self) -> str:
        pass

    @abstractmethod
    def get_code(code_id: str) -> CodeInfo:
        pass