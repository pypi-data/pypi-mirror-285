import csv
import hashlib
import json
import logging
import os
from typing import Iterator, List

import pandas as pd
from db_copilot.contract import EmbeddingDocument, EmbeddingResult, EmbeddingService


class DummyEmbeddingService(EmbeddingService):
    def __init__(self):
        self.documents = pd.DataFrame(columns=["Metadata", "Chunk"])

    def build_index(self, docs: Iterator[EmbeddingDocument], **kwargs) -> None:
        for doc in docs:
            self.documents = pd.concat(
                [
                    self.documents,
                    pd.DataFrame(
                        {
                            "Metadata": json.dumps(
                                {
                                    "source": {
                                        "filename": hashlib.md5(
                                            f"{json.dumps(doc.meta)}-{doc.text}".encode()
                                        ).hexdigest()
                                    },
                                    "meta": doc.meta,
                                }
                            ),
                            "Chunk": doc.text,
                        },
                        index=[0],
                    ),
                ],
                ignore_index=True,
                axis=0,
            )

    def search(self, query: str, top_k: int, **kwargs) -> List[EmbeddingResult]:
        return []

    def dump(self, folder: str, chunk_size: int = 10):
        if not os.path.exists(folder):
            os.makedirs(folder)
        for i, chunk in enumerate(
            self.documents.groupby(self.documents.index // chunk_size)
        ):
            output_file = os.path.join(folder, f"Chunks_{i}.csv")
            chunk[1].to_csv(output_file, index=False, quoting=csv.QUOTE_ALL)
            logging.info(f"saved grounding chunk file to {output_file}")
        logging.info(f"saved grounding chunk file to {folder}")
