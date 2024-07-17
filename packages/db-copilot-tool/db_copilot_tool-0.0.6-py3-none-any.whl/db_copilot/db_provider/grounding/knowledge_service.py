"""
Service to retrieve knowledge pieces from the given database based on 
"""
from typing import List, Tuple, Iterator
import logging
from collections import defaultdict

from db_copilot.contract import KnowledgePiece, EmbeddingService, EmbeddingDocument
from db_copilot.db_provider.utils import StopWatcher

logger = logging.getLogger("knowledge_service")

class KnowledgeService:
    def __init__(self, knowledge_pieces: List[KnowledgePiece], embedding_service: EmbeddingService, top_k_factor: int=3, build_index: bool=True) -> None:
        self.knowledge_pieces = knowledge_pieces
        docs = self._convert_to_embedding_documents(knowledge_pieces)
        self.embedding_service = embedding_service
        self.top_k_factor = top_k_factor

        if build_index:
            sw = StopWatcher()
            self.embedding_service.build_index(docs)
            logger.info("{} build index for {} knowledge pieces over, cost = {}ms.".format(self.embedding_service.__class__.__name__, len(docs), sw.elapsed_ms()))


    def retrieve(self, query: str, top_k: int, **kwargs) -> List[Tuple[KnowledgePiece, float]]:
        results = self.embedding_service.search(query, int(top_k * self.top_k_factor), **kwargs)
        priority2pieces = defaultdict(list)
        for result in results:
            index = result.document.meta['id']
            priority = result.document.meta['priority']
            priority2pieces[priority].append((self.knowledge_pieces[index], result.score))
        
        # Return results by priority
        pieces_with_score = []
        for _, pieces in sorted(priority2pieces.items(), key=lambda x: x[0]):
            pieces_with_score += pieces
        return pieces_with_score[:top_k]

    def _convert_to_embedding_documents(self, knowledge_pieces: List[KnowledgePiece]) -> Iterator[EmbeddingDocument]:
        docs = []
        for i, piece in enumerate(knowledge_pieces):
            doc = EmbeddingDocument(
                text=piece.get_embedding_text(),
                meta={ 'id': i, 'priority': piece.priority }
            )
            docs.append(doc)
        return docs

