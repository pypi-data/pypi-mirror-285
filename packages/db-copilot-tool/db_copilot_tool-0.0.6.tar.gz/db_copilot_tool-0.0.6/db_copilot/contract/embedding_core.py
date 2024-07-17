from abc import ABC, abstractmethod
from typing import List, Dict, Iterator
from dataclasses import dataclass

@dataclass
class EmbeddingDocument:
    text: str
    meta: Dict[str, str]


@dataclass
class EmbeddingResult:
    score: float
    document: EmbeddingDocument


class EmbeddingModel(ABC):
    def get_embeddings(self, texts: List[str], **kwargs) -> List:
        pass


class EmbeddingService(ABC):
    @abstractmethod
    def build_index(self, docs: Iterator[EmbeddingDocument], **kwargs) -> None:
        pass
    
    @abstractmethod
    def search(self, query: str, top_k: int, **kwargs) -> List[EmbeddingResult]:
        pass

