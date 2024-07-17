from typing import List, Callable
import logging

import faiss

from db_copilot.contract import EmbeddingDocument, EmbeddingResult, EmbeddingModel, EmbeddingService


class FaissEmbeddingService(EmbeddingService):
    def __init__(self, embedding_model: EmbeddingModel, l2_normalize: bool=True, text_process_func: Callable=None) -> None:
        super().__init__()
        self.embedding_model = embedding_model
        self.l2_normalize = l2_normalize
        self.text_process_func = text_process_func

        self.faiss_index: faiss.Index = None
        self.docs: List[EmbeddingDocument] = None
    
    @classmethod
    def from_documents(cls, embedding_model: EmbeddingModel, documents: List[EmbeddingDocument], **kwargs) -> "FaissEmbeddingService":
        """
        Create an embedding service from the given documents and an embedding model
        """
        args = {k: v for k, v in kwargs.items() if k in ('l2_normalize', 'text_process_func')}
        service = cls(embedding_model=embedding_model, **args)
        service.build_index(documents, **kwargs)
        return service


    def search(self, query: str, top_k: int, **kwargs) -> List[EmbeddingResult]:
        assert self.faiss_index is not None, "Index not found. Please run `build_index` with your documents set before search."

        # Get query embedding and normalize for cosine similarity
        query_embedding = self.embedding_model.get_embeddings([query])
        faiss.normalize_L2(query_embedding)

        scores, indices = self.faiss_index.search(query_embedding, k=top_k)

        results = []
        for idx, score in zip(indices[0], scores[0]):
            result = EmbeddingResult(score=score, document=self.docs[idx])
            results.append(result)

        return results

    def build_index(self, docs: List[EmbeddingDocument], **kwargs) -> None:
        self.docs = docs

        def _get_embedding_text(doc: EmbeddingDocument) -> str:
            emb_text = doc.text if hasattr(doc, 'text') else str(doc)
            if self.text_process_func:
                emb_text = self.text_process_func(emb_text)
            return emb_text

        doc_embeddings = self.embedding_model.get_embeddings(
            [_get_embedding_text(doc) for doc in docs],
            **kwargs
        )

        faiss_index = faiss.index_factory(doc_embeddings.shape[1], "Flat", faiss.METRIC_INNER_PRODUCT)
        
        # Normalize for cosine similarity
        if self.l2_normalize:
            faiss.normalize_L2(doc_embeddings)

        faiss_index.add(doc_embeddings)

        logging.info("Build index for %d documents over.", doc_embeddings.shape[0])
        self.faiss_index = faiss_index