from typing import Callable, List

import azureml.rag.embeddings as rag_embeddings
from azureml.rag.embeddings import EmbeddingsContainer
from db_copilot_tool.telemetry import track_function


@track_function(name="GroundingServiceManager:get_embeddings_container")
def get_embeddings_container(embed_func: Callable[[str], List[float]]):
    assert callable(embed_func)

    def embed_fn(texts: List[str], **kwargs) -> List[List[float]]:
        return [embed_func(text) for text in texts]

    # patch rag_embeddings
    rag_embeddings.get_embed_fn = lambda *args, **kwargs: embed_fn
    rag_embeddings.get_query_embed_fn = lambda *args, **kwargs: embed_fn
    embeddings_container = EmbeddingsContainer(
        kind="azure",
        dimensions=1024,
    )
    return embeddings_container
