import json
from abc import ABC, abstractclassmethod
from dataclasses import dataclass
from typing import List, Tuple

import pandas as pd

from db_copilot.contract.chat_core import Message
from db_copilot.contract.llm_core import LLM
from db_copilot.contract.tool_core import Cell, PythonExecuteResult


# TODO: is the following code enought to convert a dataframe to known types?
def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    for column in df.columns:
        for c_type in [float, str]:
            try:
                df[column] = df[column].astype(
                    c_type)
                break
            except ValueError:
                continue
            except TypeError:
                try:
                    df[column] = df[column].astype(str)
                    break
                except ValueError:
                    continue

    return df


def get_sampled_values(df: pd.DataFrame, topk=5):
    sampled_values = ['Here are some sampled values for some columns:']
    for column in df.columns:
        try:
            sampled_values.append(
                f'{column} {json.dumps(df[column].value_counts().index[:topk].tolist())}')
        except Exception:
            continue
    return '\n'.join(sampled_values)+'\n'


# conversation history
def get_history_prompt(msg_history: List[Message]) -> str:
    if not msg_history:
        return ''
    return 'Below are the dialogue histories that you can leverage to fully understand current user query:\n'\
        + '\n'.join([f"{turn.role.value}: {turn.content}" for turn in msg_history])+'\n'


# response generated so far in current turn
def get_current_prompt(cells: List[Cell]) -> str:
    if not cells:
        return ''
    # the last cell is the generated python code for user reference.
    return 'Here is the explanation of how the dataframe is generated:\n'\
        + ''.join([cell.content for cell in cells[:-1]])+'\n'


def get_analysis_prompt_common(df: pd.DataFrame, msg_history: List[Message], cells: List[Cell], prefix: str = 'You are a data analyst, the input is a python pandas DataFrame df, with following columns:') -> str:
    return f"""
{prefix}
{json.dumps(df.columns.tolist())}
-------------
{get_sampled_values(df)}
-------------
{get_current_prompt(cells)}
-------------
""".strip()


@dataclass
class AnalysisExecuteResult(PythonExecuteResult):
    analysis_evidences: List[Tuple[str, str]] = None

    def as_prompt_text(self, **kwargs) -> str:
        if self.data is None:
            return self.exception_message
        return self.data


class Analyzer(ABC):
    """
    Abstract class for analysers
    """

    def __init__(self, query: str, llm: LLM, msg_history: List[Message], cells: List[Cell]) -> None:
        super().__init__()
        self.query = query
        self.llm = llm
        self.msg_history = msg_history
        self.cells = cells

    @abstractclassmethod
    def get_analysis_info(self, df: pd.DataFrame, evidences: List[Tuple[str, str]], **kwargs) -> str:
        """
        Analyse the data
        """
        pass

    def get_base_prompt(self, df: pd.DataFrame, prefix=None) -> str:
        if prefix:
            return get_analysis_prompt_common(df, self.msg_history, self.cells, prefix)
        return get_analysis_prompt_common(df, self.msg_history, self.cells)
