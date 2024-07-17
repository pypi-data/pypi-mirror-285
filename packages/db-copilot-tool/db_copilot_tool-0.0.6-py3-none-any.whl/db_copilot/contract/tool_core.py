from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from .generic import DictMixin, PromptMixin
from .data_core import TableData
from .llm_core import PromptComposer
from .utils.text_utils import lstrip_text, rstrip_text


@dataclass
class CodeBlock(DictMixin):
    source: str = None

    @classmethod
    def from_dict(cls, obj: Dict) -> "CodeBlock":
        return super().from_dict(obj)


@dataclass
class CodeExecuteResult(ABC, DictMixin, PromptMixin):
    cost_ms: int = None # execution cost in ms
    exception_message: str = None

    @classmethod
    def from_dict(cls, obj: Dict) -> "CodeExecuteResult":
        return super().from_dict(obj)


@dataclass
class SQLExecuteResult(CodeExecuteResult):
    data: TableData = None

    @classmethod
    def from_dict(cls, obj: Dict) -> "SQLExecuteResult":
        if "data" in obj and obj["data"] is not None:
            obj["data"] = TableData.from_dict(obj["data"])
        return super().from_dict(obj)

    def as_prompt_text(self, **kwargs) -> str:
        if self.data is None:
            return f'<ErrorMessage>\n{self.exception_message}\n</ErrorMessage>' # let the model know there is an error explicitly and retry it again.
        else:
            return self.data.as_prompt_text()

_PROMPT_FOR_FIGURE_OUTPUT = '# This is a figure and has been visualized to the user.'
_PROMPT_FOR_DATAFRAME_OUTPUT = '# This is a table data frame and has been presented to the user.'


@dataclass
class PythonExecuteResult(CodeExecuteResult):
    data: Union[int, float, str, bool, dict] = None
    std_output: str = None

    @classmethod
    def from_dict(cls, obj: Dict) -> "PythonExecuteResult":
        return super().from_dict(obj)

    def as_prompt_text(self, **kwargs) -> str:
        if self.exception_message:
            return self.exception_message
        output_lst = [self.std_output.strip()] if \
            self.std_output is not None and self.std_output.strip() else []
        if self.data:
            # result text for LLM prompt in case of figure/dataframe presented
            if isinstance(self.data, TableData):
                output_lst.append(self.data.as_prompt_text())
            else:
                output_lst.append(_PROMPT_FOR_FIGURE_OUTPUT)

        return '\n'.join(output_lst)

@dataclass
class CodeInfo(DictMixin):
    code_id: str
    code_type: str
    code_block: CodeBlock
    code_execute_result: Optional[CodeExecuteResult]

    @classmethod
    def from_dict(cls, obj: Dict) -> "CodeInfo":
        obj["code_block"] = CodeBlock.from_dict(obj["code_block"])
        if "code_execute_result" in obj and obj["code_execute_result"] is not None:
            try:
                obj["code_execute_result"] = SQLExecuteResult.from_dict(obj["code_execute_result"])
            except:
                obj["code_execute_result"] = PythonExecuteResult.from_dict(obj["code_execute_result"])
        return super().from_dict(obj)
    
@dataclass
class Cell(DictMixin):
    content: str
    code_info: Optional[CodeInfo]

    @classmethod
    def from_dict(cls, obj: Dict) -> "Cell":
        if "code_info" in obj and obj["code_info"]:
            obj["code_info"] = CodeInfo.from_dict(obj["code_info"])
        else:
            obj["code_info"] = None
        return super().from_dict(obj)
    
    def as_prompt_text(self, start_symbol: str, end_symbol: str, include_execution_result=True) -> str:
        if self.code_info is None:
            return f"""{start_symbol}
{rstrip_text(lstrip_text(self.content, start_symbol), end_symbol)}
{end_symbol}
""".strip()
        
        result_text = ''
        if include_execution_result and self.code_info.code_execute_result:
            result_text = f"\n{self.code_info.code_execute_result.as_prompt_text()}".rstrip()

        return f"""{start_symbol}
```{self.code_info.code_type} code_id='{self.code_info.code_id}'
{self.code_info.code_block.source.strip()}
```{result_text}
{end_symbol}
""".strip()


@dataclass
class Tool(ABC):
    def __init__(self, prompt_template: str = None):
        self.prompt_template = prompt_template

    @abstractmethod
    def execute(self, code: CodeBlock, **kwargs: Any) -> CodeExecuteResult:
        pass

    @property
    @abstractmethod
    def prompt_text(self) -> Union[str, PromptComposer]:
        pass
