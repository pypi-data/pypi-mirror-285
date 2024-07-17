"""
LLM interface
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Union
from enum import Enum

class LLMType(str, Enum):
    UnKnown = "unknown"
    GPT35_TURBO = "gpt-3.5-turbo"
    GPT4_DV3 = "gpt-4-dv3"
    GPT4_PPO = "gpt-4-ppo"

class PromptComposer(ABC):
    @abstractmethod
    def compose(self, llm_type: LLMType):
        pass

class LLM(ABC):
    def __init__(self, llm_type: LLMType):
        self.llm_type = llm_type

    @abstractmethod
    def chat(self, messages: List[Dict], prompt: Union[str, PromptComposer], stop: List[str], stream: bool, **kwargs: Any) -> Iterator[str]:
        pass
