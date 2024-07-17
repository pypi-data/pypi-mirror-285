from functools import partial
from typing import List, Tuple

import pandas as pd

from db_copilot.analysis.analysis_com import (AnalysisExecuteResult, Analyzer,
                                              get_analysis_prompt_common,
                                              preprocess_dataframe)
from db_copilot.analysis.auto_analyzer import AutoAnalyzer
from db_copilot.analysis.ols_analyzer import OrdinaryLeastSquaresAnalyzer
from db_copilot.contract.api_core import APIManager
from db_copilot.contract.chat_core import Message
from db_copilot.contract.llm_core import LLM
from db_copilot.contract.tool_core import Cell, CodeBlock
from db_copilot.tool import Tool


class AnalyzerCollection(Analyzer):
    def __init__(self, analyzers: List[Analyzer] = None):
        self.analyzers: List[Analyzer] = analyzers

    def get_analysis_info(self, df: pd.DataFrame, evidences: List[Tuple[str, str]], **kwargs) -> str:
        prompt = ['The analysis information we collected:']
        # TODO: run in parallel
        for analyser in self.analyzers:
            prompt.append(analyser.get_analysis_info(df, evidences, **kwargs))
        return "\n---------\n".join(prompt)


class AnalysisTool(Tool):
    BLOCK_START = 'python_data_analysis'

    def __init__(self, query: str, llm: LLM, db_type: str, msg_history: List[Message]) -> None:
        self.query = query
        self.llm = llm
        # TODO: is db_type a must ?
        self.db_type = db_type
        self.msg_history = msg_history[-4:] if msg_history else None

    def get_analysis_result(self, df: pd.DataFrame, cells: List[Cell]) -> str:
        df = preprocess_dataframe(df)

        analyzer = AnalyzerCollection(
            analyzers=[
                AutoAnalyzer(self.query, self.llm, self.msg_history, cells),
                # OrdinaryLeastSquaresAnalyzer(
                #     self.query, self.llm, self.msg_history, cells)
            ]
        )
        evidences = []
        analysis_info = analyzer.get_analysis_info(
            df, evidences)

        analysis_response = next(self.llm.complete(prompt=self.prompt_text_inner(
            df, cells, analysis_info), stop=['<|im_end|>'], stream=False))
        return AnalysisExecuteResult(data=analysis_response, analysis_evidences=evidences)

    def execute(self,
                code: CodeBlock,
                cells: List[Cell],
                **kwargs
                ) -> AnalysisExecuteResult:        
        l = locals()
        try:
            # TODO: streaming
            python_vars = { api: kwargs[api] for api in APIManager.get_api_names() if api in kwargs}
            python_vars['get_analysis_result'] = partial(self.get_analysis_result, cells=cells)
            exec(code.source, python_vars, l)
            return l['analysis_results']
        except Exception as e:
            return AnalysisExecuteResult(data=None, exception_message=str(e))

    def prompt_text_inner(self, df: pd.DataFrame, cells: List[Cell], analysis_info: str) -> str:
        return f"""
{get_analysis_prompt_common(df, self.msg_history, cells)}
-------------
{analysis_info}
-------------
Given the above information, please answer the user query in a way that people without statistics background can understand, the user query is:
{self.query}
""".strip()

    @property
    def prompt_text(self):
        return f"""
This is a data analysis tool, you can use this tool to perform data analysis after the data is retrieved from the database using the {self.db_type} tool.
This tool support data analysis for user queries like "why", "what causes", "what if", "predictive", and queries for suggestions etc. The following questions are typical examples:
    - why the active users are decreasing in the last month?
    - what causes the sales to increase in the last month?
    - what if we increase the price of the product by 10%?
    - what if we increase the price of the product and decrease the discount by 5%?
    - any suggestions to increase the sales?
    - suggest a goal for next three months
This tool provide get_analysis_result API to perform data analysis, before using this API, you need to get dataframe from previous SQL execution results, e.g., `df = {APIManager.GET_CODE_RESULT.template.format(code_id=1)}` or `df = {APIManager.GET_CODE_RESULT.template.format(code_id=2)}`. Note that, the code_id is the code_id of the previous SQL code block. You can find the code_id in the previous history or current response. We can not leverage the code execution result if the code_id does not exist in previous history or current response.
You can generate the following code wrapped by ```{AnalysisTool.BLOCK_START} to use this tool:
```{AnalysisTool.BLOCK_START}
df = {APIManager.GET_CODE_RESULT.template.format(code_id=1)}
analysis_results = get_analysis_result(df)
```
get_analysis_result is a predefined function that takes a dataframe as input and returns a string as output. The string contains the analysis results. Do not generate the code for get_analysis_result, it is predefined and you should not modify it.
""".strip()
