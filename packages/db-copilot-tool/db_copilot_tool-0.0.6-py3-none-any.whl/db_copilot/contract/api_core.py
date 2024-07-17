from dataclasses import dataclass
from typing import List

@dataclass
class API:
    name: str
    signature: str
    description: str
    template: str
    
    def as_prompt_text(self) -> str:
        return f"""
Python API - {self.name}: {self.description}.
- Signature: `{self.signature}`
"""

class APIManager:
    GET_CODE_RESULT = API("get_code_result", "def get_code_result(code_id: str) -> CodeExecuteResult", "Get the result of one existing code execution", "get_code_result(code_id='{code_id}')")

    @staticmethod
    def as_prompt_text() -> str:
        return f"""
You can use following python APIs when you write python code:
- You don't need to write code_id for your code.
- When you see code_id in the session context, you can use the API to reuse its result.
{APIManager.GET_CODE_RESULT.as_prompt_text()}
"""

    @staticmethod
    def get_api_names() -> List[str]:
        return [APIManager.GET_CODE_RESULT.name]