from enum import Enum
import json
from typing import Any


class LoggingType(str, Enum):
    LLM_REQUEST = "LLM REQUEST"
    LLM_RESPONSE = "LLM RESPONSE"

    def msg(self, metadata: Any) -> str:
        return json.dumps(
            {
                'type': self.value,
                'metadata': metadata
            }
        )