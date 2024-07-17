from functools import lru_cache
from typing import Iterator, List, Tuple
import copy
from datetime import date
from db_copilot.contract.chat_core import DialogueAgent, DialogueResponse, InContextExample, InContextLearningAgent
from db_copilot.contract.api_core import APIManager
from db_copilot.contract.memory_core import MemoryManager, MemoryItem, MessageRole, Message
from db_copilot.contract.db_core import DBSnapshot
from db_copilot.contract.db_provider import DBProviderAgent
from db_copilot.contract.tool_core import Cell, CodeInfo
from db_copilot.contract.plan_core import Planner
from db_copilot.contract.llm_core import PromptComposer
from db_copilot.memory_manager import DefaultMemoryManager
from db_copilot.follow_up import FollowUpQueryRewriteSkill
from db_copilot.prompts.instruct import INSTRUCT_TEMPLATES, DEFAULT_INSTRUCT_TEMPLATE
from db_copilot.suggestion import SuggestionGenerationSkill
from db_copilot.llm import DynamicPromptComposer, StaticPromptComposer, CompoundPromptComposer
from db_copilot.telemetry import get_logger, track_activity
logger = get_logger("db_copilot.dialogue_agent")

class DefaultDialogueAgent(DialogueAgent):
    def __init__(
            self,
            db_provider_agent: DBProviderAgent,
            in_context_learning_agent: InContextLearningAgent,
            planner: Planner,
            follow_up_skill: FollowUpQueryRewriteSkill,
            suggestion_skill: SuggestionGenerationSkill = None,
            instruct_template: str = None,
            num_prompt_examples: int = 4,
            prompt_generation_args: dict = None,
            memory_manager: MemoryManager = None,
            timeout: float = 600.0
        ) -> None:
        self.db_provider_agent = db_provider_agent
        self.in_context_learning_agent = in_context_learning_agent
        self.planner = planner
        self.instruct_template = instruct_template
        self.follow_up_skill = follow_up_skill
        self.suggestion_skill = suggestion_skill
        self.num_prompt_examples = num_prompt_examples
        self.prompt_generation_args = prompt_generation_args if prompt_generation_args is not None else {}
        self.memory_manager = memory_manager if memory_manager is not None else DefaultMemoryManager()
        self.timeout = timeout

    def interact(
            self,
            question: str,
            memory: List[MemoryItem],
            temperature: float = None,
            top_p: float = None,
            timeout: float = None,
            **kwargs
        ) -> Iterator[DialogueResponse]:
        with track_activity(logger, "agent interact") as activity_logger:
            activity_logger.info("initialize memory started")
            self.memory_manager.init(memory)
            activity_logger.info("initialize memory completed")

            activity_logger.info("build prompt started")

            additional_information=kwargs.pop('additional_information', '')
            prompt_composer, messages = self._build_prompt_str(
                question=question,
                num_prompt_examples=self.num_prompt_examples,
                additional_information=additional_information,
                **kwargs)
            activity_logger.info("build prompt completed")

            activity_logger.info("call planner started")
            cells_generator = self.planner.generate(
                prompt=prompt_composer,
                memory_manager=self.memory_manager,
                temperature=temperature,
                top_p=top_p,
                messages=messages,
                timeout=timeout or self.timeout,
                **kwargs)
            cells = []
            for tmp_cells in cells_generator:
                # for incomplete responses, no need to return memory
                yield DialogueResponse(tmp_cells, [])
                cells = tmp_cells
            activity_logger.info("call planner completed")
            self._update_memory(question, cells)
            yield DialogueResponse(cells, self.memory_manager.get_memory())

    def suggest(
            self,
            question: str,
            memory: List[MemoryItem],
            num: int = 3,
            creative: bool = False
    ) -> List[str]:
        assert self.suggestion_skill is not None, "Suggestion skill is not provided in the dialogue agent."

        user_msg_history = [x.content for x in memory if x.role == MessageRole.USER]
        if question is not None:
            followup_question = self.follow_up_skill.generate(question, memory)
            user_msg_history.append(followup_question)
            grounding_result: DBSnapshot = self._grounding(followup_question)
        else:
            grounding_result: DBSnapshot = self._grounding(None)
        return self.suggestion_skill.generate(grounding_result.as_prompt_text(), user_msg_history, num, creative)
    
    @lru_cache
    def _grounding(self, question: str, **kwargs) -> DBSnapshot:
        with track_activity(logger, "grounding") as activity_logger:
            return self.db_provider_agent.retrieve_schema(question, **kwargs)

    def _build_prompt_str(self,
                         question: str,
                         num_prompt_examples,
                         additional_information,
                         **kwargs
                         ) -> Tuple[PromptComposer, List]:
        with track_activity(logger, "followup") as activity_logger:
            followup_question = self.follow_up_skill.generate(question, self.memory_manager.get_memory())
        grounding_result: DBSnapshot = self._grounding(followup_question, **kwargs)

        query = InContextExample(embed_text=followup_question, prompt_text=None)
        examples_prompt_text = '... (examples)'
        if self.in_context_learning_agent:
            examples: List[InContextExample] = self.in_context_learning_agent.similarity_search(query=query, top_k=num_prompt_examples, schema=grounding_result.as_prompt_text(**self.prompt_generation_args), **kwargs)
            examples_prompt_text = '\n\n'.join([f"========= Example Session {idx} =========\n{example.prompt_text}\n" for idx, example in enumerate(examples)])
        
        messages, memory_prompt_text = self._build_memory_prompt_text(question)
        messages.append(Message(role= MessageRole.USER, content= f'<Question>{question}</Question>'))
        api_prompt_text = APIManager.as_prompt_text()
        grounding_prompt_text=grounding_result.as_prompt_text(**self.prompt_generation_args)
        
        tool_prompt_composer = self.planner.prompt_text
        if isinstance(tool_prompt_composer, str):
            tool_prompt_composer = StaticPromptComposer(tool_prompt_composer)

        def format_instruct(template: str):
            return CompoundPromptComposer(
                template=template,
                param_composers=dict(
                    followup_question=StaticPromptComposer(followup_question),
                    api_prompt_text=StaticPromptComposer(api_prompt_text),
                    examples_prompt_text=StaticPromptComposer(examples_prompt_text),
                    grounding_prompt_text=StaticPromptComposer(grounding_prompt_text),
                    tool_prompt_text=tool_prompt_composer,
                    memory_prompt_text=StaticPromptComposer(memory_prompt_text),
                    date=StaticPromptComposer(str(date.today())),
                    additional_information=StaticPromptComposer(additional_information)
                )
            )
        
        if self.instruct_template:
            return format_instruct(self.instruct_template), messages

        instruct_prompt_dict = {key: format_instruct(val) for key, val in INSTRUCT_TEMPLATES.items()}
        return DynamicPromptComposer(format_instruct(DEFAULT_INSTRUCT_TEMPLATE), instruct_prompt_dict), messages
    
    def _update_memory(self, question: str, cells: List[Cell]):
        self.memory_manager.add(MemoryItem(MessageRole.USER, question, code_infos=None))

        content = "\n".join(x.as_prompt_text(self.planner.cell_symbol_start, self.planner.cell_symbol_end, include_execution_result=False) for x in cells)
        
        def process_code(cell_code_info: CodeInfo):
            # Not cache any previous results besides the exception
            code_CoW = copy.deepcopy(cell_code_info)
            if code_CoW.code_execute_result is not None and code_CoW.code_execute_result.exception_message is None:
                code_CoW.code_execute_result = None
            return code_CoW

        code_infos = [process_code(x.code_info) for x in cells if x.code_info]
        self.memory_manager.add(MemoryItem(MessageRole.ASSISTANT, content, code_infos))
    
    def _build_memory_prompt_text(self, query: str) -> Tuple[List, str]:
        kept_memory: List[MemoryItem] = self.memory_manager.retrieve(query)

        kept_memory_msgs, exist_code_ids = list(), list()
        for item in kept_memory:
            kept_memory_msgs.append(Message(role= item.role, content = item.content.strip()))
            if item.role == MessageRole.ASSISTANT and item.code_infos:
                exist_code_ids += [f"code_id='{x.code_id}'" for x in item.code_infos]

        exist_code_id_prompt_text = ', '.join(exist_code_ids)
        
        return kept_memory_msgs, f"""
Here are a list of generated code ids that you can leverage:
- You can only get the code result that you have seen the code_id in current session
- Existing code_id list in the history: [{exist_code_id_prompt_text}]

For example,
if the last question in dialogue history is "total sales by brand"
and the current question is "pie chart",
it means that the user wants "total sales by brand as a pie chart".
""".strip()
