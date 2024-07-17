from dataclasses import asdict
from typing import List

from db_copilot.contract import InContextExample, InContextLearningAgent, EmbeddingModel, EmbeddingDocument,EmbeddingResult
from db_copilot.contract.llm_core import LLM
from db_copilot.utils import FaissEmbeddingService
from db_copilot.telemetry import get_logger
from db_copilot.telemetry.telemetry import LatencyTracker
logger = get_logger("faiss_agent")

class FaissInContextLearningAgent(InContextLearningAgent):
    def __init__(self, examples: List[InContextExample],
            embedding_model: EmbeddingModel,
            rewrite_llm: LLM=None,
            rewrite_prompt=None,
            rewrite_template=None,
        ) -> None:
        
        documents = [EmbeddingDocument(text=example.embed_text, meta=asdict(example)) for example in examples]
        with LatencyTracker() as t:
            self._faiss = FaissEmbeddingService.from_documents(embedding_model, documents=documents)
        logger.info(f"Faiss index for {len(documents)} documents created in {t.duration} seconds")

        self.rewrite_llm = rewrite_llm
        self.rewrite_prompt = rewrite_prompt
        self.rewrite_template = rewrite_template

    def similarity_search(self, query: InContextExample, top_k: int = 4, **kwargs) -> List[InContextExample]:
        if self.rewrite_llm and self.rewrite_prompt and self.rewrite_template:
            schema = kwargs.get('schema')
            query = self.rewrite(query, schema)
            
        # Get embed text from kwargs if present.
        embed_text = kwargs.get('query_embed_text', query.embed_text)

        with LatencyTracker() as t:
            results = self._faiss.search(embed_text, top_k)
        logger.info(f"Similarity search for {embed_text} executed in {t.duration} seconds")

        mandatory_examples = kwargs.get('mandatory_example', [])
    
        if mandatory_examples and len(mandatory_examples) > 0:
            self.add_mandatory_examples(results, mandatory_examples)

        return [InContextExample(**result.document.meta) for result in results]
        
    def add_mandatory_examples(self, results, mandatory_examples):
        # Iterate over each mandatory_example
        for example_text in mandatory_examples:
            matching_documents = [doc for doc in self._faiss.docs if doc.text == example_text]

            if matching_documents and len(matching_documents) > 0:
                # Take the first matching doc
                example_embedding_result = EmbeddingResult(score=0.8, document=matching_documents[0])

                # Check if example_embedding_result is not already in results based on the document.text attribute
                is_unique = True
                for result in results:
                    if (
                        result.document is not None
                        and result.document.text is not None
                        and example_embedding_result.document is not None
                        and example_embedding_result.document.text is not None
                    ):
                        if result.document.text.lower() == example_embedding_result.document.text.lower():
                            is_unique = False
                            break
                    
                if is_unique:
                    results.append(example_embedding_result)

    def rewrite(self, query: InContextExample, schema: str) -> InContextExample:
        assert self.rewrite_llm is not None
        assert self.rewrite_prompt is not None
        assert self.rewrite_template is not None
        rewrite_info = {'rewrite_prompt': self.rewrite_prompt,
                        'schema_str': schema,
                        'question': query.embed_text}
        prompt = self.rewrite_template.format_map(rewrite_info)
        rewrited_query_generator = self.rewrite_llm.chat(messages=None, prompt=prompt, max_tokens=200, stop='\n</Skill>', stream=False)
        for rewrited_query in rewrited_query_generator:
            continue
        rewrited_query = rewrited_query.split('\n')[0].strip()
        return InContextExample(embed_text=rewrited_query, prompt_text=None)


    @classmethod
    def from_question_response_session_list(
        cls,
        embedding_model: EmbeddingModel,
        question_response_session_list: List[List]
    ) -> "FaissInContextLearningAgent":
        examples = []
        for session in question_response_session_list:
            examples.append(InContextExample(
                embed_text=session[0]['embed_text'] if 'embed_text' in session[0] else session[0]['question'],
                prompt_text="\n\n".join(f"<Question>\n{item['question']}\n</Question>\n{item['response'].strip()}" for item in session)
            ))
        return cls(examples, embedding_model)
