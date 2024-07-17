"""File for the Azure Open AI Complete Models Classes."""

import logging
from typing import Any, Dict, Iterator, List, Union

from db_copilot.contract import LLM, LLMType, Message, MessageRole, PromptComposer
from promptflow.connections import AzureOpenAIConnection
from promptflow.tools.aoai import AzureOpenAI, PromptTemplate


class AOAIChatLLM(LLM):
    """AOAIChatLLM Class."""

    def __init__(
        self,
        config: AzureOpenAIConnection,
        deployment_name: str,
        max_token: int = 1024,
        temperature: float = 0.0,
        top_p: float = 0.0,
    ) -> None:
        """Initialize the class."""
        self.openai_provider = AzureOpenAI(config)
        self.deployment_name = deployment_name
        self.max_token = max_token
        self.temperature = temperature
        self.top_p = top_p

    def chat(
        self,
        messages: List[Dict],
        prompt: Union[str, PromptComposer],
        stop: List[str],
        stream: bool,
        **kargs: Any,
    ) -> Iterator[str]:
        """chat."""
        if not messages and not prompt:
            raise ValueError("Either prompt or messages must be provided")
        if prompt and isinstance(prompt, PromptComposer):
            prompt = prompt.compose(LLMType.UnKnown)
        if messages and prompt:
            messages = [
                Message(role=MessageRole.SYSTEM, content=prompt).to_dict()
            ] + messages
        elif not messages:
            messages = [Message(role=MessageRole.USER, content=prompt).to_dict()]

        full_prompt = PromptTemplate(
            "\n".join(
                [f'{message["role"]}:\n{message["content"]}' for message in messages]
            )
        )
        logging.info(f"AOAIChatLLM full_prompt: {full_prompt}")
        temperature = kargs.get("temperature") or self.temperature
        top_p = kargs.get("top_p") or self.top_p
        result = self.openai_provider.chat(
            full_prompt,
            self.deployment_name,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=0,
            presence_penalty=0,
            stop=stop,
            n=1,
            stream=False,
            max_tokens=self.max_token,
        )
        logging.info(f"AOAIChatLLM result: {result}")
        return iter([result])


class AOAICompleteLLM(LLM):
    """AOAICompleteLLM Class."""

    def __init__(
        self,
        config: AzureOpenAIConnection,
        deployment_name: str,
        max_token: int = 1024,
        temperature: float = 0.0,
        top_p: float = 0.0,
    ) -> None:
        """Initialize the class."""
        self.openai_provider = AzureOpenAI(config)
        self.deployment_name = deployment_name
        self.max_token = max_token
        self.temperature = temperature
        self.top_p = top_p

    def chat(
        self,
        messages: List[Dict],
        prompt: Union[str, PromptComposer],
        stop: List[str],
        stream: bool,
        **kargs: Any,
    ) -> Iterator[str]:
        """chat."""
        if not messages and not prompt:
            raise ValueError("Either prompt or messages must be provided")
        if prompt and isinstance(prompt, PromptComposer):
            prompt = prompt.compose(LLMType.UnKnown)
        if messages and prompt:
            messages = [
                Message(role=MessageRole.SYSTEM, content=prompt).to_dict()
            ] + messages
        elif not messages:
            messages = [Message(role=MessageRole.USER, content=prompt).to_dict()]

        full_prompt = PromptTemplate(
            "\n".join(
                [f'{message["role"]}:\n{message["content"]}' for message in messages]
            )
        )
        logging.info(f"AOAICompleteLLM full_prompt: {full_prompt}")
        temperature = kargs.get("temperature") or self.temperature
        top_p = kargs.get("top_p") or self.top_p
        result = self.openai_provider.completion(
            full_prompt,
            self.deployment_name,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=0,
            presence_penalty=0,
            stop=stop,
            n=1,
            stream=False,
            max_tokens=self.max_token,
        )
        logging.info(f"AOAICompleteLLM result: {result}")
        return iter([result])
