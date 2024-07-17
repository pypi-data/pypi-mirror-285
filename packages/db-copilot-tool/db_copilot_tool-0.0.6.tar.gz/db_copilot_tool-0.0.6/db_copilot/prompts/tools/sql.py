from db_copilot.contract.db_core import SQLDialect
from db_copilot.contract.llm_core import LLMType

DEFAULT_TOOL_TEMPLATE = """
You are connected to a database. The database schema will be provided to you later.
You can generate a markdown code block (e.g., ```{dialect}\n...\n```) to specify how to query against the database to fetch needed information.
If you get the exception information rather than execution result, it means that the generated sql query contains some issues and you should try to repair it based on the exception message.
"""

TOOL_TEMPLATES = {}

TOOL_TEMPLATES[SQLDialect.TSQL] = {}
TOOL_TEMPLATES[SQLDialect.TSQL][LLMType.GPT35_TURBO] = DEFAULT_TOOL_TEMPLATE + """
Note that:
- "SELECT xxx AS y ... GROUP BY y" is an incorrect query.
  The correct way to write the query is: "SELECT xxx AS y ... GROUP BY xxx".
  In other words, terms defined in SELECT clause cannot be directly used in GROUP BY clause.
""".strip()
TOOL_TEMPLATES[SQLDialect.TSQL][LLMType.GPT4_DV3] = TOOL_TEMPLATES[SQLDialect.TSQL][LLMType.GPT35_TURBO]
TOOL_TEMPLATES[SQLDialect.TSQL][LLMType.UnKnown] = TOOL_TEMPLATES[SQLDialect.TSQL][LLMType.GPT35_TURBO]


TOOL_TEMPLATES[SQLDialect.SQLITE] = TOOL_TEMPLATES[SQLDialect.TSQL]

TOOL_TEMPLATES[SQLDialect.KQL] = {}
TOOL_TEMPLATES[SQLDialect.KQL][LLMType.GPT35_TURBO] = DEFAULT_TOOL_TEMPLATE + """
Note that:
- Please carefully deal with datetime and numeric values when generating the kusto queries.
  Don't compare values of types int and datetime directly.
  For example, if the "year" is an int column, "last 5 years" should be: year >= (datetime_part('year', now()) - 5)
"""
TOOL_TEMPLATES[SQLDialect.KQL][LLMType.GPT4_DV3] = TOOL_TEMPLATES[SQLDialect.KQL][LLMType.GPT35_TURBO]
TOOL_TEMPLATES[SQLDialect.KQL][LLMType.UnKnown] = TOOL_TEMPLATES[SQLDialect.KQL][LLMType.GPT35_TURBO]