from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Iterator, List

from db_copilot.contract.tool_core import Cell
from db_copilot.contract.memory_core import MemoryItem


@dataclass
class DialogueResponse:
    cells: List[Cell]
    memory: List[MemoryItem]


class DialogueAgent(ABC):
    @abstractmethod
    def interact(
            self,
            question: str,
            memory: List[MemoryItem],
            temperature: float = None,
            top_p: float = None
    ) -> Iterator[DialogueResponse]:
        pass


@dataclass
class InContextExample:
    embed_text: str
    prompt_text: str


class InContextLearningAgent(ABC):
    @abstractmethod
    def similarity_search(self, query: InContextExample, top_k: int, **kwargs: Dict) -> List[InContextExample]:
        pass
