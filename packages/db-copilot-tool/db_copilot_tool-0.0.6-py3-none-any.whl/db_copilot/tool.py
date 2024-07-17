import io
import json
import sys
from typing import Any, Dict
import traceback

from db_copilot.contract import TableData
from db_copilot.contract.tool_core import (
    CodeBlock,
    PythonExecuteResult,
    SQLExecuteResult,
    Tool,
)
from db_copilot.contract.db_provider import DBProviderAgent
from db_copilot.prompts.tools.plotly import (
    TOOL_TEMPLATES as PLOTLY_TEMPLATES,
    DEFAULT_TOOL_TEMPLATE as DEFAULT_PLOTLY_TEMPLATE,
)
from db_copilot.prompts.tools.sql import (
    TOOL_TEMPLATES as SQL_TEMPLATES,
    DEFAULT_TOOL_TEMPLATE as DEFAULT_SQL_TEMPLATE,
)
from db_copilot.contract.api_core import APIManager
from db_copilot.llm import StaticPromptComposer, DynamicPromptComposer
from db_copilot.utils import preprocess_dataframe
from db_copilot.telemetry import get_logger
from db_copilot.telemetry.telemetry import LatencyTracker

logger = get_logger("db_copilot.tool")


class PythonExecuteTool(Tool):
    def __init__(self, prompt_template: str = None, additional_imports: Dict = {}):
        self.additional_imports = additional_imports
        super().__init__(prompt_template)

    def execute(self, code: CodeBlock, **kwargs: Any) -> PythonExecuteResult:
        memory = kwargs["memory"]
        l = {}
        try:
            import pandas as pd
            import plotly.express as px

            python_vars = {
                api: kwargs[api] for api in APIManager.get_api_names() if api in kwargs
            }

            def print_to_result(*args, sep="", end="\n"):
                line = sep.join([f"{arg}" for arg in args]) + end
                if "std_output" not in l:
                    l["std_output"] = list()
                l["std_output"].append(line)

            python_vars["preprocess_dataframe"] = preprocess_dataframe
            python_vars["pd"] = pd
            python_vars["px"] = px
            python_vars["json"] = json
            python_vars["print"] = print_to_result
            if self.additional_imports:
                python_vars.update(self.additional_imports)
            python_vars["memory"] = memory
            with LatencyTracker() as t:
                exec(code.source, python_vars, l)
            logger.info(f"This code {code.source} executed in {t.duration} seconds")
            res = l.get("res")
            if res is None:
                if "fig" in l and hasattr(l.get("fig"), "to_json"):
                    res = l.get("fig").to_json()
                else:
                    res = l.get("df")
            if res is not None:
                import plotly.graph_objects as go

                if isinstance(res, go.Figure):
                    res = json.loads(res.to_json())
                elif "highcharts" in code.source:
                    res = {"data": res}
                    res["chart_lib"] = "highcharts"
                elif isinstance(res, TableData):
                    pass
                elif isinstance(res, pd.DataFrame):
                    res = TableData.from_df(res)
                else:
                    res = json.loads(res)
            std_output = None
            if "std_output" in l:
                std_output = "".join(l["std_output"])
                logger.info(f"Std output: {std_output}")
            return PythonExecuteResult(data=res, std_output=std_output)
        except Exception as e:
            trace_msg = traceback.format_exc()
            logger.error(
                f"Error executing code: {code.source}\nException occurs: {type(e).__name__}: {str(e)}\n{trace_msg}"
            )
            return PythonExecuteResult(data=None, exception_message=trace_msg)

    @property
    def prompt_text(self):
        if self.prompt_template:
            return StaticPromptComposer(self.prompt_template)

        default_composer = StaticPromptComposer(DEFAULT_PLOTLY_TEMPLATE)
        prompt_dict = {
            key: StaticPromptComposer(val) for key, val in PLOTLY_TEMPLATES.items()
        }
        return DynamicPromptComposer(default_composer, prompt_dict)


class SQLExecuteTool(Tool):
    def __init__(
        self, db_provider: DBProviderAgent, prompt_template: str = None
    ) -> None:
        self.db_provider = db_provider
        super().__init__(prompt_template)

    def execute(self, code: CodeBlock, **kwargs: Any) -> SQLExecuteResult:
        try:
            return self.db_provider.execute_code(code)
        except Exception as e:
            return SQLExecuteResult(data=None, exception_message=str(e))

    @property
    def prompt_text(self):
        def format_template(template: str):
            return StaticPromptComposer(
                template.format(dialect=self.db_provider.sql_dialect)
            )

        if self.prompt_template:
            return format_template(self.prompt_template)

        if self.db_provider.sql_dialect not in SQL_TEMPLATES:
            return format_template(DEFAULT_SQL_TEMPLATE)

        default_composer = format_template(DEFAULT_SQL_TEMPLATE)
        prompt_dict = {
            key: format_template(val)
            for key, val in SQL_TEMPLATES[self.db_provider.sql_dialect].items()
        }
        return DynamicPromptComposer(default_composer, prompt_dict)
