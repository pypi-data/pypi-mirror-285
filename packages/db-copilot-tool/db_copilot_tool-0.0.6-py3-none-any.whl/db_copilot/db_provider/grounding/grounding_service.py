import logging
import pickle
from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property
from typing import Callable, Dict, Iterator, List, Tuple

from db_copilot.contract import (DBSnapshot, DictMixin, EmbeddingDocument,
                                 EmbeddingModel, EmbeddingResult,
                                 EmbeddingService, TableData, TableSchema,
                                 TableSnapshot)
from db_copilot.contract.utils import StopWatcher
from db_copilot.db_provider.db_executor import DBExecutor
from db_copilot.db_provider.utils import (camel_case_normalize, distinct_list,
                                          split_into_short)
from db_copilot.telemetry import get_logger, track_activity
from db_copilot.utils import FaissEmbeddingService

from .grounding_context import ConceptType, DBConcept, GroundingContext
from .hybrid_embedding import HybridEmbeddingService
from .knowledge_service import KnowledgePiece, KnowledgeService

logger = get_logger("db_copilot.grounding")

@dataclass
class GroundingConfig(DictMixin):
    max_tables: int = 10
    max_columns: int = 10
    max_rows: int = 3
    max_sampling_rows: int = 200
    max_text_length: int = 200
    max_knowledge_pieces: int = 10

    encode_dependency: bool = False
    ngram_hybrid_weight: float = None
    split_query_into_short: int = None

    max_tokens: int = None # not supported yet

    def __post_init__(self):
        assert self.max_tables >= 1, "number of tables >= 1"

    def estimate_concepts(self, alpha: int=3) -> int:
        return min(2000, int(self.max_tables * self.max_columns * self.max_rows * alpha))

    @property
    def enable_hybrid_embedding(self) -> bool:
        return self.ngram_hybrid_weight and self.ngram_hybrid_weight > 1e-3
    
    def clone(self) -> "GroundingConfig":
        return self.__class__.from_dict(self.to_dict())


@dataclass
class InternalTableSnapshot(TableSnapshot):
    data_frame = None
    columns: List = None
    rows: List = None
    column_to_rows: Dict[str, List] = None

    def resolve(self, context: GroundingContext, max_cols: int, max_rows: int, **kwargs) -> TableSnapshot:

        grounding_prompt_style = kwargs.get("grounding_prompt_style")
        # Always append primary key columns
        kept_core_cols = self.schema.primary_key + self.columns + self.schema.foreign_columns
        num_kept_cols = max(max_cols, len(kept_core_cols))
        sel_cols = distinct_list(kept_core_cols + [c.name for c in self.schema.columns])[:num_kept_cols]

        value_data = context.sample_data[self.schema.name]
        assert len(value_data.columns) == len(self.schema.columns)

        sel_cols_with_types = [(c, d_type, i) for i, (c, d_type) in enumerate(zip(value_data.columns, value_data.column_types)) if c in sel_cols]
        sel_cols = [x[0] for x in sel_cols_with_types]
        sel_col_indices = [x[2] for x in sel_cols_with_types]

        max_sel_rows = min(value_data.num_rows, max_rows) 

        data, columns_selected,column_selected_types = None, None, None

        if grounding_prompt_style == 'distinct_values':
            distinct_value_data, distinct_value_col_indices = self.get_distinct_value_snapshot(sel_cols, sel_col_indices, max_sel_rows, value_data)
            data = distinct_value_data
            columns_selected = [value_data.columns[i] for i in distinct_value_col_indices]
            column_selected_types = [value_data.column_types[i] for i in distinct_value_col_indices]
        else:
            sel_rows = distinct_list(self.rows + list(range(max_sel_rows)))[:max_sel_rows]
            row_data = []
            for r_idx in sel_rows:
                row = value_data.data[r_idx]
                sel_row = [row[i] for i in sel_col_indices]
                row_data.append(sel_row)
            data = row_data
            columns_selected = sel_cols
            column_selected_types = [x[1] for x in sel_cols_with_types]

        snapshot_data = TableData(
            columns=columns_selected,
            column_types=column_selected_types,
            data=data
        )

        return TableSnapshot(
            schema=self.schema,
            data_frame=snapshot_data
        )
    
    def get_distinct_value_snapshot(self, sel_cols : List[str], sel_col_indices : List[int], max_sel_rows : int, value_data : TableData):
        distinct_columns = []
        new_col_indices = []
        for i in range(len(sel_cols)):
            curr_col = sel_cols[i]
            # The order of column will preserve, and it has to present in the column_to_rows lookup
            if curr_col not in self.column_to_rows:
                continue
            distinct_columns.append(self.column_to_rows[curr_col])
            new_col_indices.append(sel_col_indices[i])

        snapshot = []
        for i in range(max_sel_rows):
            # adding the row index, note the row index here doesn't mean the row index in the database
            temp = [i + 1]
            for j in range(len(distinct_columns)):
                # if the column doesn't have enough distinct values, we will fill the rest with none
                if i >= len(distinct_columns[j]):
                    temp.append(None)
                else:
                    temp.append(value_data.data[distinct_columns[j][i]][new_col_indices[j]])
            snapshot.append(temp)
        # the row_id column is always at 0, adding the row_id index
        new_col_indices = [0] + new_col_indices
        return snapshot, new_col_indices

def get_table_full_text_as_documents(table_schemas: Dict[str, TableSchema]):
    documents = []
    for tbl_name, tbl_schema in table_schemas.items():
        column_names = [c.name for c in tbl_schema.columns]
        table_full_text = "{}: {}".format(tbl_name, " | ".join(column_names))
        document = EmbeddingDocument(
            text=table_full_text,
            meta={ 'table_name': tbl_name }
        )
        
        documents.append(document)

    return documents


def long_query_optimize_decorator(func: Callable, ngrams: int=8):
    """
    Optimize long-query searching by splitting raw query into multiple sub-queries and then merging the results
    """
    def wrapper(*args, **kwargs):
        query, top_k = args[0], args[1]
        sub_queries = split_into_short(query, ngrams=ngrams)
        logger.info("split input query into {} sub queries: {}".format(len(sub_queries), sub_queries))

        concept2results: Dict[str, EmbeddingResult] = {}
        for sub_query in sub_queries:
            emb_results = func(sub_query, top_k, **kwargs)
            for result in emb_results:
                c_id = result.document.meta.get("id")
                if c_id not in concept2results:
                    concept2results[c_id] = result
                else:
                    concept2results[c_id].score = max(result.score, concept2results[c_id].score)
        
        merged_results = list(sorted(concept2results.items(), key=lambda x: x[1].score, reverse=True))[:top_k]
        concept_results = [x[1] for x in merged_results]
        return concept_results[:top_k]
    
    return wrapper


def limit_max_values_decorator(func: Callable, max_values_per_column: int=8):
    def wrapper(*args, **kwargs):
        emb_results: List[EmbeddingResult] = func(*args, **kwargs)
        new_results = []
        column_values_cnt = defaultdict(int)
        for result in emb_results:
            c_type = result.document.meta.get("type")
            column = result.document.meta.get("parent")
            if c_type != "value":
                new_results.append(result)
                continue
            
            if column_values_cnt[column] >= max_values_per_column:
                continue

            column_values_cnt[column] += 1
            new_results.append(result)

        if len(new_results) < len(emb_results):
            logger.info("{} value results are filtered due to max values limit ({})".format(len(emb_results) - len(new_results), max_values_per_column))
        return new_results
    
    return wrapper


@dataclass
class GroundingService:
    config: GroundingConfig
    context: GroundingContext
    embedding_service: EmbeddingService
    knowledge_service: KnowledgeService = None

    @property
    def service_id(self) -> str:
        return self.context.context_id

    def search(self, query: str, **kwargs) -> DBSnapshot:
        processed_query = self.preprocess(query)
        
        emb_results = self._search_concepts(
            query=processed_query,
            top_k=self.config.estimate_concepts(3),
        )

        knowledge_pieces_with_scores = None
        if self.knowledge_service:
            # Avoid embedding
            if len(self.knowledge_service.knowledge_pieces) <= self.config.max_knowledge_pieces:
                knowledge_pieces_with_scores = [
                    (piece, 0.0) for piece in self.knowledge_service.knowledge_pieces
                ]
            else:
                knowledge_pieces_with_scores = self.knowledge_service.retrieve(
                    query=processed_query,
                    top_k=self.config.max_knowledge_pieces
                )

        db_snapshot = self.post_process(emb_results, knowledge_pieces_with_scores, **kwargs)
        
        return db_snapshot
    
    def _search_concepts(self, query: str, top_k: int, **kwargs):
        concept_results = self.embedding_service.search(query, top_k, context=self.context)
        return concept_results
    
    @staticmethod
    def preprocess(text: str) -> str:
        return camel_case_normalize(text)
    
    @cached_property
    def default_db_snapshot(self) -> DBSnapshot:
        table_snapshots = [
            InternalTableSnapshot(schema=table_schema, data_frame=None, columns=[c.name for c in table_schema.columns], rows=[]) \
                .resolve(self.context, max_cols=len(table_schema.columns), max_rows=3)
            for _, table_schema in self.context.table_schemas.items()
        ]
        return DBSnapshot(db_type=self.context.db_type, table_snapshots=table_snapshots)
    
    def post_process(self, embedding_results: List[EmbeddingResult], knowledge_pieces_with_scores: List[Tuple[KnowledgePiece, float]]=None, **kwargs) -> DBSnapshot:
        # entity knowledge scores
        concept_knowledge_scores: Dict[int, float] = defaultdict(float)
        if knowledge_pieces_with_scores:
            for piece, score in knowledge_pieces_with_scores:
                if not piece.entities:
                    continue
                for concept_id in piece.entities:
                    concept_knowledge_scores[concept_id] = max(score, concept_knowledge_scores.get(concept_id, 0.0))
            
            if concept_knowledge_scores:
                concept2results = {
                    result.document.meta.get("id"): result
                    for result in embedding_results
                }

                for concept_id, score in concept_knowledge_scores.items():
                    if concept_id in concept2results:
                        concept2results[concept_id].score = max(concept2results[concept_id].score, score)
                    else:
                        concept2results[concept_id] = EmbeddingResult(score, self.context.concepts[concept_id].to_document())
                
                # Re-sort after updating scores
                embedding_results = list(sorted(concept2results.values(), key=lambda x: x.score, reverse=True))

        # Sort results with structure dependency
        concept_results = self.generate_constraint_results(embedding_results)

        table2snapshots: dict[str, InternalTableSnapshot] = {}
        for concept, _ in concept_results:
            parents = self.context.lookup_parent_concepts(concept, reverse=True)

            # Table
            if concept.type == ConceptType.TABLE:
                tbl_schema: TableSchema = concept.schema
                table2snapshots[tbl_schema.name] = InternalTableSnapshot(schema=tbl_schema, data_frame=None, columns=[], rows=[], column_to_rows={})
            
            # Column
            if concept.type == ConceptType.COLUMN:
                if parents[0].schema.name in table2snapshots:
                    table2snapshots[parents[0].schema.name].columns.append(concept.schema.name)
            
            # Value
            if concept.type == ConceptType.VALUE:
                curr_snapshot = table2snapshots[parents[0].schema.name]
                if parents[0].schema.name in table2snapshots and \
                    parents[1].schema.name in curr_snapshot.columns:
                    curr_snapshot.rows.append(concept.schema)
                    
                    if parents[1].schema.name in curr_snapshot.column_to_rows:
                        curr_snapshot.column_to_rows[parents[1].schema.name].append(concept.schema)
                    else:
                        curr_snapshot.column_to_rows[parents[1].schema.name] = [concept.schema]

        table2snapshots = self.enrich_reference_relations(table2snapshots)

        table_snapshots = []
        for tbl_name in self.context.table_schemas:
            if tbl_name not in table2snapshots:
                continue
            snapshot = table2snapshots[tbl_name].resolve(self.context, self.config.max_columns, self.config.max_rows, **kwargs)
            table_snapshots.append(snapshot)

        knowledge_pieces = [x for x, _ in knowledge_pieces_with_scores] if knowledge_pieces_with_scores else None
        return DBSnapshot(db_type=self.context.db_type, table_snapshots=table_snapshots, knowledge_pieces=knowledge_pieces)
    
    def enrich_reference_relations(self, table2snapshots: Dict[str, InternalTableSnapshot]) -> Dict[str, InternalTableSnapshot]:
        # Try to add  more relevant referenced tables to ensure SQL join operation works
        core_table_names = { x.schema.name  for x in table2snapshots.values()}
        all_referenced_tables = defaultdict(int)
        for tbl_name, tbl_schema in self.context.table_schemas.items():
            if tbl_name in core_table_names:
                for fk_table in tbl_schema.referenced_tables:
                    all_referenced_tables[fk_table] += 1
            
            for fk_table in tbl_schema.referenced_tables:
                if fk_table in core_table_names:
                    all_referenced_tables[tbl_name] += 1
        
        for tbl_name, ref_cnt in sorted(all_referenced_tables.items(), key=lambda x: x[1], reverse=True):
            tbl_schema = self.context.table_schemas.get(tbl_name, None)
            if tbl_name in table2snapshots or len(table2snapshots) >= self.config.max_tables or tbl_schema is None:
                continue

            logging.info("Add default table `{}` to enrich reference relations, referenced count: {}.".format(tbl_name, ref_cnt))
            table2snapshots[tbl_name] = InternalTableSnapshot(schema=tbl_schema, data_frame=None, columns=[], rows=[])

        return table2snapshots

    def convert_to_concept_results(self, embedding_results: List[EmbeddingResult]) -> Iterator[Tuple[DBConcept, float]]:
        concepts = set([])
        for embedding_result in embedding_results:
            concept = self.context.lookup_concept(embedding_result.document.meta.get("id"))
            if concept.id in concepts:
                continue

            parents = self.context.lookup_parent_concepts(concept, reverse=True)
            for parent in parents:
                if parent.id in concepts:
                    continue

                concepts.add(parent.id)
                yield parent, embedding_result.score
            
            concepts.add(concept.id)
            yield concept, embedding_result.score

    def generate_constraint_results(self, embedding_results: List[EmbeddingResult]):
        # Generate concept results with constraint
        concept_results: Dict[str, Tuple[DBConcept, float]] = {}
        type_statistics = defaultdict(int)

        id2scores = {
            r.document.meta.get("id"): r.score
            for r in embedding_results
        }

        def _add_concept_result(concept: DBConcept):
            if concept.id in concept_results:
                return True
            
            max_limit = { 
                ConceptType.TABLE: self.config.max_tables,
                ConceptType.COLUMN: self.config.max_columns,
                ConceptType.VALUE: self.config.max_rows 
            }[concept.type]

            if type_statistics[concept.parent] >= max_limit:
                return False
            
            type_statistics[concept.parent] += 1
            concept_results[concept.id] = (concept, id2scores.get(concept.id, -1.0))
            return True

        for embedding_result in embedding_results:
            concept = self.context.lookup_concept(embedding_result.document.meta.get("id"))

            parent_added = True
            for parent in self.context.lookup_parent_concepts(concept, reverse=True):
                if not _add_concept_result(parent):
                    parent_added = False
                    break
            
            if parent_added:
                _add_concept_result(concept)
        
        sorted_results = [r for _, r in concept_results.items()]
        return sorted_results

    @classmethod
    def build_from_db_executor(cls, 
        db_id: str,
        db_executor: DBExecutor,
        embedding_service: EmbeddingService=None,
        embedding_model: EmbeddingModel=None,
        config: GroundingConfig=None,
        knowledge_pieces: List[KnowledgePiece] = None,
        build_index: bool=True,
        **kwargs
    ) -> "GroundingService":
        
        with track_activity(logger, "build_grounding_service") as activity_logger:
            # Setup grounding config
            if isinstance(config, dict):
                config = GroundingConfig.from_dict(config)

            # Use default
            config = config if config is not None else GroundingConfig()
            # Keep unique config for different databases
            config = config.clone()

            sw = StopWatcher()
            if kwargs.get("context_pkl_path", None):
                with open(kwargs["context_pkl_path"], 'rb') as fr:
                    context = pickle.load(fr)
            else:
                context = GroundingContext.from_db_executor(
                    db_id=db_id,
                    db_executor=db_executor,
                    max_sampling_rows=config.max_sampling_rows,
                    max_text_length=config.max_text_length
                )
            
            cost1 = sw.elapsed_ms()
            activity_logger.activity_info["context_build_elapsed_ms"] = cost1
            logger.info("Build grounding context over, cost: {}ms.".format(cost1))
            
            # set to max if the `max_tables` or `max_columns` is `None` to keep consistent
            table2columns = context.get_table_to_columns()
            if config.max_tables is None:
                config.max_tables = len(table2columns)
            if config.max_columns is None:
                config.max_columns = max([len(columns) for _, columns in table2columns.items()])

            if embedding_service is None:
                assert embedding_model is not None, "embedding model is required to create embedding service"
                embedding_service = FaissEmbeddingService(embedding_model, text_process_func=cls.preprocess)
                logger.info("Create default Faiss embedding service over.")

            embedding_service.search = limit_max_values_decorator(embedding_service.search, max_values_per_column=min(config.max_rows * 2, config.max_rows + 3))
            
            if config.split_query_into_short and config.split_query_into_short > 0:
                embedding_service.search = long_query_optimize_decorator(embedding_service.search, ngrams=config.split_query_into_short)
                logger.info("Wrap concept embedding service `search` with `long_query_optimize_decorator` over.")
            
            # Use hybrid embedding service
            if config.enable_hybrid_embedding:
                embedding_service = HybridEmbeddingService(
                    embedding_service=embedding_service,
                    ngram_weight=config.ngram_hybrid_weight,
                    text_process_func=cls.preprocess
                )
                logger.info("Wrap concept embedding service with ngram hybrid mode, weight: {:.3f}".format(config.ngram_hybrid_weight))
            
            if build_index:
                documents=[c.to_document(context=context, encode_dependency=config.encode_dependency) for c in context.concepts]
                embedding_service.build_index(documents, **kwargs)
                logger.info("{} build index for {} documents over!".format(embedding_service.__class__.__name__, len(documents)))
            
            cost2 = sw.elapsed_ms() - cost1
            activity_logger.activity_info["embedding_service_build_elapsed_ms"] = cost2
            logger.info("Build concept embedding service over, cost: {}ms.".format(cost2))

            knowledge_service: KnowledgeService = None
            if knowledge_pieces:
                knowledge_embedding_service = kwargs.get("knowledge_embedding_service", None)
                if knowledge_embedding_service is None:
                    knowledge_embedding_model = kwargs.get("knowledge_embedding_model", embedding_model)
                    assert knowledge_embedding_model is not None, "embedding model is required to create default knowledge embedding service"
                    knowledge_embedding_service = FaissEmbeddingService(knowledge_embedding_model, text_process_func=cls.preprocess)

                if config.split_query_into_short and config.split_query_into_short > 0:
                    knowledge_embedding_service.search = long_query_optimize_decorator(knowledge_embedding_service.search, ngrams=config.split_query_into_short)
                    logger.info("Wrap knowledge embedding service `search` with `long_query_optimize_decorator` over.")
            
                # Use hybrid embedding service
                if config.enable_hybrid_embedding:
                    knowledge_embedding_service = HybridEmbeddingService(
                        embedding_service=knowledge_embedding_service,
                        ngram_weight=config.ngram_hybrid_weight,
                        text_process_func=cls.preprocess
                    )
                    logger.info("Wrap knowledge embedding service with ngram hybrid mode, weight: {:.3f}".format(config.ngram_hybrid_weight))

                knowledge_pieces = list(sorted(knowledge_pieces, key=lambda x: x.priority))
                entity2concepts = context.entity_to_concepts
                for piece in knowledge_pieces:
                    if not piece.entities:
                        continue
                    
                    concepts = []
                    for entity in piece.entities:
                        if entity in entity2concepts:
                            concepts.append(entity2concepts[entity])
                        else:
                            logger.warn('Entity `{}` not found in DB schema, please ensure the full name is correct.'.format(entity))
                    
                    piece.entities = concepts

                knowledge_service = KnowledgeService(
                knowledge_pieces=knowledge_pieces,
                embedding_service=knowledge_embedding_service,
                build_index=build_index
                )
            
            cost3 = sw.elapsed_ms() - cost2 - cost1
            activity_logger.activity_info["knowledge_service_build_elapsed_ms"] = cost3
            logger.info("Build knowledge service over, cost: {}ms.".format(cost3))

            grounding_service = GroundingService(
                config=config,
                context=context,
                embedding_service=embedding_service,
                knowledge_service=knowledge_service
            )

            logger.info("Build grounding service over, cost: {}ms.".format(sw.elapsed_ms()))
            return grounding_service
