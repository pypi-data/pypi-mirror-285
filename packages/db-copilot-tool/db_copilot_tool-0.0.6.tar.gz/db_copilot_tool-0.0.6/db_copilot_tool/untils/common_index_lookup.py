import logging
import os
from typing import List

from promptflow_vectordb.tool.common_index_lookup import search
from promptflow_vectordb.tool.common_index_lookup_utils import forward_mapping


class CommonIndexLookup:
    """CommonIndexLookup is a wrapper class for search function in common_index_lookup.py"""

    def __init__(self, index_type: str = None, query_type: str = None, **kwargs):
        try:
            self.index_type = index_type
            self.kwargs = kwargs
            self.query_type = query_type

            subscription_id = os.environ.get("AZUREML_SUBSCRIPTION_ID", None)
            resource_group = os.environ.get("AZUREML_RESOURCE_GROUP", None)
            workspace_name = os.environ.get("AZUREML_WORKSPACE_NAME", None)
            self.mlindex_content = forward_mapping(
                subscription_id=subscription_id,
                resource_group_name=resource_group,
                workspace_name=workspace_name,
                index_type=self.index_type,
                **self.kwargs,
            )
        except Exception as ex:
            logging.error(f"Error in initializing CommonIndexLookup: {ex}")
            raise ex

    def search(self, query: str, top_k: int = 10):
        """Search for the top_k most similar documents to the given vector."""
        try:
            search_results = search(
                mlindex_content=self.mlindex_content,
                queries=query,
                top_k=top_k,
                query_type=self.query_type,
            )
            return search_results
        except Exception as ex:
            logging.error(f"Error in CommonIndexLookup search: {ex}")
            logging.error(f"Query content: {query}")
            raise ex
