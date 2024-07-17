import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterator, List, Tuple, Union
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import backoff
from openai import AzureOpenAI
import requests
import sys
from openai import (
    APIError,
    RateLimitError,
    APIConnectionError,
    InternalServerError,
    APITimeoutError,
)

from db_copilot.contract.llm_core import LLM, LLMType, PromptComposer
from db_copilot.contract.memory_core import Message, MessageRole
from db_copilot.telemetry import get_logger, track_activity

logger = get_logger("db_copilot.llm")


@dataclass
class StaticPromptComposer(PromptComposer):
    prompt: str

    def compose(self, llm_type: LLMType):
        return self.prompt


@dataclass
class DynamicPromptComposer(PromptComposer):
    default_prompt: PromptComposer
    prompt_dict: Dict[LLMType, PromptComposer] = None

    def compose(self, llm_type: LLMType):
        if self.prompt_dict and llm_type in self.prompt_dict:
            return self.prompt_dict[llm_type].compose(llm_type)

        return self.default_prompt.compose(llm_type)


@dataclass
class CompoundPromptComposer(PromptComposer):
    template: str
    param_composers: Dict[str, PromptComposer]
    post_process_func: Callable[[str], str] = None

    def compose(self, llm_type: LLMType):
        params = {
            key: val.compose(llm_type) for key, val in self.param_composers.items()
        }
        prompt = self.template.format(**params)
        if self.post_process_func:
            return self.post_process_func(prompt)

        return prompt


def format_messages(messages: List[Dict]) -> str:
    lines = []
    for msg in messages:
        lines.append("Role: {}".format(str(msg["role"]).upper()))
        lines.append("Content: {}".format(msg["content"]))
    return "\n".join(lines)


# https://platform.openai.com/docs/guides/gpt/managing-tokens
def num_tokens_from_messages(messages: Union[List[Dict], str]):
    import tiktoken

    encoding = tiktoken.get_encoding("cl100k_base")
    if isinstance(messages, str):
        return len(encoding.encode(messages))
    num_tokens = 0
    for message in messages:
        num_tokens += (
            4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        )
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":  # if there's a name, the role is omitted
                num_tokens += -1  # role is always required and always 1 token
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens


class OpenAIBackoffHandler:
    def __init__(
        self, max_tries: int = 3, delay: float = 1.0, show_msg_callback=logger.warning
    ) -> None:
        assert max_tries > 0, "Invalid max_tries: {}".format(max_tries)
        self.max_tries = max_tries
        self.delay = delay
        self.callback = show_msg_callback

    @property
    def backoff_exception(self) -> Tuple[Exception]:
        return (
            RateLimitError,
            InternalServerError,
            APIError,
            APITimeoutError,
            APIConnectionError,
            requests.exceptions.ConnectionError,
        )

    def on_exception(self, details: Dict):
        e = details["exception"]
        self.callback(f"Exception occurs: {type(e).__name__}: {str(e)}")
        logger.error(
            f"Exception occurs: {type(e).__name__}: {str(e)}, here is the details: {details}"
        )
        if isinstance(e, RateLimitError):
            self.callback(f"sleeping for {self.delay} seconds for RateLimitError")
            time.sleep(self.delay)

    def on_giveup(self, details: Dict[str, Any]) -> None:
        elapsed: float = details['elapsed']
        tries: int = details['tries']
        _, exc_value, _ = sys.exc_info()
        assert exc_value is not None
        raise exc_value

    def on_success(self, details: Dict):
        pass


class OpenaiChatLLM(LLM):
    def __init__(
        self,
        llm_type: LLMType,
        api_base: str,
        model: str,
        api_key: str = None,
        api_type: str = "azure",
        api_version: str = "2023-07-01-preview",
        max_tokens: int = 1024,
        temperature: float = 0.0,
        top_p: float = 0.0,
        headers: dict = None,
        calculate_token_usage: bool = True,
        backoff_handler: OpenAIBackoffHandler = None,
    ):
        super().__init__(llm_type)
        assert api_type == "azure"
        self.api_type = api_type
        self.api_version = api_version
        self.api_base = api_base
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.headers = headers if headers else {}
        self.calculate_token_usage = calculate_token_usage
        # Use default backoff handler if not provided
        self.backoff_handler = (
            backoff_handler if backoff_handler else OpenAIBackoffHandler()
        )

    def fill_messages(
        self, messages: List[Dict], prompt: Union[str, PromptComposer], **kwargs
    ) -> List[Dict]:
        if not messages and not prompt:
            raise ValueError("Either prompt or messages must be provided")
        if prompt and isinstance(prompt, PromptComposer):
            prompt = prompt.compose(self.llm_type)
        if messages and prompt:
            messages = [
                Message(role=MessageRole.SYSTEM, content=prompt).to_dict()
            ] + messages
        elif not messages:
            messages = [Message(role=MessageRole.USER, content=prompt).to_dict()]

        return messages

    def submit_completion(self, messages: List[Dict], chat_args: Dict) -> Dict:
        if self.api_key:
            client = AzureOpenAI(
                azure_endpoint=self.api_base,
                api_key=self.api_key,
                api_version=self.api_version,
            )
        else:
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
            )
            logger.info("Using AAD token for authentication.")
            client = AzureOpenAI(
                azure_endpoint=self.api_base,
                api_version=self.api_version,
                azure_ad_token_provider=token_provider,
            )

        resp = client.chat.completions.create(messages=messages, **chat_args)
        return resp

    def chat(
        self,
        messages: List[Union[Dict, Message]],
        prompt: Dict[str, PromptComposer],
        stop: List[str],
        stream: bool,
        **kwargs: Any,
    ) -> Iterator[str]:
        with track_activity(logger, "llm_chat") as activity_logger:
            prompt_tokens = 0
            completion_tokens = 0
            messages = self.fill_messages(messages, prompt, **kwargs)
            chat_args = {
                "model": self.model,
                "temperature": kwargs.get("temperature") or self.temperature,
                "top_p": kwargs.get("top_p") or self.top_p,
                "timeout": kwargs.get("timeout"),
                "max_tokens": self.max_tokens,
                "stream": stream,
                "stop": stop,
                "seed": 666,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "n": 1,
            }
            activity_logger.activity_info.update(chat_args)
            activity_logger.activity_info["num_messages"] = len(messages)
            logger.info(
                "{}, Messages:\n{}".format(chat_args, format_messages(messages))
            )

            backoff_submit_completion = backoff.on_exception(
                backoff.expo,
                self.backoff_handler.backoff_exception,
                max_tries=kwargs.get("max_tries") or self.backoff_handler.max_tries,
                on_backoff=self.backoff_handler.on_exception,
                on_giveup=self.backoff_handler.on_giveup,
                on_success=self.backoff_handler.on_success,
            )(self.submit_completion)

            resp = backoff_submit_completion(messages, chat_args)

            result = ""
            if stream:
                buffer = []
                for chunk in resp:
                    # logger.info("Chunk: %s", chunk.model_dump_json(indent=4))
                    if chunk and chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if delta and delta.content:
                            buffer.append(delta.content)
                            if len(buffer) == 5:
                                yield "".join(buffer)
                                result += "".join(buffer)
                                buffer = []
                if len(buffer) > 0:
                    yield "".join(buffer)
                    result += "".join(buffer)
                logger.info("Response: %s", result)
                if self.calculate_token_usage:
                    if self.llm_type not in [
                        LLMType.GPT35_TURBO,
                        LLMType.GPT4_DV3,
                        LLMType.GPT4_PPO,
                    ]:
                        raise ValueError("Invalid LLM type: {}".format(self.llm_type))
                    prompt_tokens = num_tokens_from_messages(messages)
                    completion_tokens = num_tokens_from_messages(result)
            else:
                yield resp.choices[0].message.content
                result = resp.choices[0].message.content
                if "usage" in resp:
                    prompt_tokens = resp.usage["prompt_tokens"]
                    completion_tokens = resp.usage["completion_tokens"]

            logger.info("Result: %s", result)
            if self.calculate_token_usage:
                activity_logger.activity_info.update(
                    {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                    }
                )


# deprecated, use OpenaiChatLLM
class DedicatedAmlLLM(LLM):
    def __init__(
        self,
        llm_type: LLMType,
        api_url: str,
        tenant_id: str,
        additional_headers: dict = {},
        max_tokens: int = 1024,
        temperature: float = 0.0,
        top_p: float = 0.0,
        n_retry: int = 2,
    ) -> None:
        from azure.identity import (
            ChainedTokenCredential,
            ManagedIdentityCredential,
            AzureCliCredential,
        )

        self.api_url = api_url
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.token = None
        self.token_expiry = None
        self.azure_credential = ChainedTokenCredential(
            ManagedIdentityCredential(), AzureCliCredential(tenant_id=tenant_id)
        )
        self.azure_endpoint = "https://ml.azure.com"
        self.additional_headers = additional_headers
        self.n_retry = n_retry
        super().__init__(llm_type)

    def chat(
        self,
        messages: List[Dict],
        prompt: Union[str, PromptComposer],
        stop: List[str],
        stream: bool,
        **kwargs: Any,
    ) -> Iterator[str]:
        raise NotImplementedError()

    def get_token(self) -> str:
        if self.token_invalid() or self.credential_expired():
            access_token = self.azure_credential.get_token(self.azure_endpoint)
            self.token = access_token.token
            self.token_expiry = access_token.expires_on
        return self.token

    def token_invalid(self) -> bool:
        return self.token is None

    def credential_expired(self) -> bool:
        return self.token_expiry is None or time.time() >= self.token_expiry


# deprecated, use OpenaiChatLLM
class AzureOAICompletionLLM(DedicatedAmlLLM):
    def __init__(
        self,
        llm_type: LLMType,
        api_url: str,
        tenant_id: str,
        deployment: str,
        max_tokens: int = 1024,
        temperature: float = 0.0,
        top_p: float = 0.0,
    ) -> None:
        super().__init__(
            llm_type,
            api_url,
            tenant_id,
            {
                "azureml-model-deployment": deployment,
                "Openai-Internal-AllowedSpecialTokens": "<|im_start|>,<|im_sep|>,<|im_end|>,<|start|>,<|message|>,<|end_message|>,<|end_message_and_sample_again|>,<|end_message_done_sampling|>,<|startoftext|>,<|endoftext|>,<|fim_prefix|>,<|fim_middle|>,<|fim_suffix|>,<|meta_start|>,<|meta_end|>,<|meta_sep|>,<|im_start|>,<|im_end|>,<|im_sep|>,<|disc_score|>,<|ipynb_marker|>,<|diff_marker|>,<|ghissue|>,<|ghreview|>,<|disc_sep|>,<|disc_thread|>,<|endoffile|>,<|disc_score_mid|>,<|endofprompt|>",
                "Openai-Internal-AllowChatCompletion": "1",
                "Openai-Internal-HarmonyVersion": "harmony_v4.0_no_system_message_content_type",
            },
            max_tokens,
            temperature,
            top_p,
        )

    def chat(
        self,
        messages: List[Dict],
        prompt: Union[str, PromptComposer],
        stop: List[str],
        stream: bool,
        **kwargs: Any,
    ) -> Iterator[str]:
        return super().chat(messages, prompt, stop, stream, **kwargs)


class ChainLLM(LLM):
    def __init__(self, llms: List[LLM]) -> None:
        self.llms = llms
        super().__init__(LLMType.UnKnown)

    def chat(
        self,
        messages: List[Dict],
        prompt: Union[str, PromptComposer],
        stop: List[str],
        stream: bool,
        **kwargs: Any,
    ) -> Iterator[str]:
        for i, llm in enumerate(self.llms):
            try:
                for x in llm.chat(messages, prompt, stop, stream, **kwargs):
                    yield x
                break
            except (RateLimitError, requests.exceptions.HTTPError) as err:
                if i == len(self.llms) - 1:
                    raise err
