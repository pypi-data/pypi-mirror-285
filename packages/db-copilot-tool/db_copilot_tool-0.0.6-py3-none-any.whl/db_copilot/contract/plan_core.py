from abc import ABC, abstractmethod
from typing import Iterator, List, Union

from db_copilot.contract.llm_core import PromptComposer
from db_copilot.contract.tool_core import Cell
from db_copilot.contract.memory_core import MemoryManager, Message


class Planner(ABC):
    @abstractmethod
    def generate(self,
                 prompt: Union[str, PromptComposer],
                 memory_manager: MemoryManager,
                 messages: List[Message] = None,
                 temperature: float = None,
                 top_p: float = None,
                 **kwargs
                ) -> Iterator[List[Cell]]:
        pass

    @property
    @abstractmethod
    def prompt_text(self) -> Union[str, PromptComposer]:
        pass

    @property
    def cell_symbol_start(self) -> str:
        return '<Cell>'

    @property
    def cell_symbol_end(self) -> str:
        return '</Cell>'

    @property
    def response_symbol_start(self) -> str:
        return '<Response>'

    @property
    def response_symbol_end(self) -> str:
        return '</Response>'

    @property
    def stop_symbols(self) -> List[str]:
        return [
            '```\n',
            f'{self.cell_symbol_start}\nThe End\n{self.cell_symbol_end}',
            self.response_symbol_end
        ]
