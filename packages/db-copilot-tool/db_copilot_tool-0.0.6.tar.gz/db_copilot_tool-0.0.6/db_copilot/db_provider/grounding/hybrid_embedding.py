from typing import List, Callable
import logging
from db_copilot.contract import EmbeddingService, EmbeddingDocument, EmbeddingResult

from .grounding_context import GroundingContext
from .ngram_index import NGramIndex

logger = logging.getLogger("hybrid_embedding")

class HybridEmbeddingService(EmbeddingService):
    def __init__(self, embedding_service: EmbeddingService, ngram_weight: float, text_process_func: Callable=None) -> None:
        super().__init__()
        self.embedding_service = embedding_service
        self.ngram_index: NGramIndex = None
        self.documents = None
        self.ngram_weight = ngram_weight
        self.text_process_func = text_process_func
    
    def build_index(self, docs: List[EmbeddingDocument], **kwargs) -> None:
        self.embedding_service.build_index(docs, **kwargs)
        self.documents = docs
        doc_texts = []
        for doc in docs:
            doc_id = doc.meta.get('id', None)
            assert doc_id is not None, 'document must have id field to enable hybrid embedding'
            doc_texts.append(self.text_process_func(doc.text) if self.text_process_func else doc.text)
        
        logger.info("Build ngram index ...")
        self.ngram_index = NGramIndex.from_texts(doc_texts, max_ngram_tokens=kwargs.get("max_ngram_tokens", 5))
        logger.info("Build ngram index over.")

    def search(self, query: str, top_k: int, **kwargs) -> List[EmbeddingResult]:
        logger.info("Query({}): {}".format(top_k, query))
        results = self.embedding_service.search(query, top_k, **kwargs)
        results_map = {
            result.document.meta.get('id'): result
            for result in results
        }

        ngram_results = self.ngram_index.search(query, top_k=top_k)
        
        for doc_id, ngram_score in ngram_results:
            if doc_id in results_map:
                results_map[doc_id].score = results_map[doc_id].score + self.ngram_weight * ngram_score
            else:
                results_map[doc_id] = EmbeddingResult(
                    score=self.ngram_weight * ngram_score,
                    document=self.documents[doc_id]
                )
            
            results_map[doc_id].document.meta["ngram_score"] = ngram_score
        
        sorted_results = sorted(results_map.items(), key=lambda x: x[1].score, reverse=True)
        sorted_results = [x[1] for x in sorted_results][:top_k]
        context: GroundingContext = kwargs.get("context", None)
        for rk, result in enumerate(sorted_results[:200]):
            concept_id = result.document.meta.get('id')
            concept = [result.document.meta.get("type", None), result.document.text]
            if context is not None:
                parents = context.lookup_parent_concepts(concept_id, reverse=True) + [context.lookup_concept(concept_id)]
                concept = [c.name for c in parents]
            logger.info("Rank {}, score = {:.3f}/{:.3f}, text = {}/{}".format(rk, result.score, result.document.meta.get("ngram_score", 0.0), concept_id, concept))

        return sorted_results
