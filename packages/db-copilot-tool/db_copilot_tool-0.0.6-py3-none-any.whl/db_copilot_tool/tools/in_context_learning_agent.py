"""File for the InContextLearningAgent Class."""

import json
import logging
import os
from dataclasses import asdict
from typing import Dict, List, Union

import yaml
from db_copilot.contract import (
    DatabaseType,
    EmbeddingDocument,
    InContextExample,
    SQLDialect,
)
from db_copilot.in_context_learning.faiss import FaissInContextLearningAgent
from db_copilot.prompts.examples.base import convert_sessions, get_examples
from db_copilot_tool.contracts.embedding_config import EmbeddingConfig
from db_copilot_tool.tools.azureml_asset_handler import DatastoreDownloader


class InContextLearningAgent(FaissInContextLearningAgent):
    """InContextLearningAgent Class."""

    def __init__(
        self,
        embedding_config: EmbeddingConfig,
        examples: List[InContextExample] = None,
        rewrite_llm=None,
        rewrite_prompt=None,
        rewrite_template=None,
    ):
        self.embedding_service = embedding_config.embedding_service
        self._faiss = self.embedding_service
        if examples and len(examples) > 0:
            documents = (
                EmbeddingDocument(text=example.embed_text, meta=asdict(example))
                for example in examples
            )
            self._faiss.build_index(documents)
        self.rewrite_llm = rewrite_llm
        self.rewrite_prompt = rewrite_prompt
        self.rewrite_template = rewrite_template

    @staticmethod
    def get_examples(
        example_uri: str,
        db_type: DatabaseType,
        tools: Union[Dict[str, object], List[str], None] = None,
        include_built_in: bool = True,
    ):
        if example_uri:
            if example_uri.startswith("azureml://"):
                with DatastoreDownloader(example_uri) as sample_folder:
                    return InContextLearningAgent.get_examples_from_local(
                        dialect=SQLDialect.from_db_type(db_type),
                        sample_folder=sample_folder,
                        tools=tools,
                        include_built_in=include_built_in,
                    )
            elif os.path.exists(example_uri):
                return InContextLearningAgent.get_examples_from_local(
                    dialect=SQLDialect.from_db_type(db_type),
                    sample_folder=example_uri,
                    tools=tools,
                    include_built_in=include_built_in,
                )
            else:
                raise ValueError(f"Example uri {example_uri} is not valid.")
        else:
            return InContextLearningAgent.get_examples_from_local(
                dialect=SQLDialect.from_db_type(db_type),
                tools=tools,
                include_built_in=include_built_in,
            )

    @staticmethod
    def get_examples_from_local(
        dialect: SQLDialect,
        sample_folder: str = None,
        tools: Union[None, List[str], Dict[str, object]] = None,
        include_built_in: bool = True,
    ):
        if isinstance(tools, dict):
            tools = list(tools.keys())
        with_extensions = (
            True
            if tools
            and len([tool for tool in tools if tool.lower() != dialect.value]) > 0
            else False
        )
        examples = (
            get_examples(dialect, with_extensions=with_extensions)
            if include_built_in
            else []
        )
        if sample_folder:

            def load_sample_internal(sample_folder: str):
                for file in os.listdir(sample_folder):
                    try:
                        with open(os.path.join(sample_folder, file), "r") as example:
                            if file.endswith(".yaml") or file.endswith(".yml"):
                                examples_obj = yaml.safe_load(example)
                            else:
                                examples_obj = json.load(example)
                            if isinstance(examples_obj, list):
                                for example_obj in examples_obj:
                                    if example_obj.get("question", None):
                                        example = convert_sessions([[example_obj]])[0]
                                    else:
                                        example = InContextExample(**example_obj)
                                    examples.append(example)
                            elif isinstance(examples_obj, dict):
                                if examples_obj.get("question", None):
                                    example = convert_sessions([[examples_obj]])[0]
                                else:
                                    example = InContextExample(**examples_obj)
                                examples.append(example)
                            else:
                                raise ValueError(
                                    f"Invalid sample file format: {examples_obj}"
                                )
                    except Exception as ex:
                        logging.warning(
                            f"Failed to load sample file {file}. Error: {ex}"
                        )

            logging.info(f"sample folder is {sample_folder}")
            if sample_folder.startswith("azureml"):
                with DatastoreDownloader(sample_folder) as local_sample_folder:
                    load_sample_internal(local_sample_folder)
            elif os.path.exists(sample_folder):
                load_sample_internal(sample_folder)
            else:
                raise ValueError(f"Invalid sample folder: {sample_folder}")
        return examples
