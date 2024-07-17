from typing import List, Dict
from db_copilot.contract.memory_core import MemoryManager, MemoryItem
from db_copilot.contract.tool_core import CodeInfo

class DefaultMemoryManager(MemoryManager):
    def __init__(self):
        self.has_initialized = False

    def init(self, items: List[MemoryItem]):
        self.memory: List[MemoryItem] = list()
        self._latest_code_id = 0
        self._id2code: Dict[str, CodeInfo] = {}
    
        for item in items:
            self._add(item, update_latest_code_id=True)
        
        self.has_initialized = True

    def _check(self):
        if not self.has_initialized:
            raise Exception("Memory manager should be initialized firstly")

    def _add(self, item: MemoryItem, update_latest_code_id: bool):
        if item.code_infos is not None:
            for code in item.code_infos:
                if code.code_id in self._id2code:
                    raise Exception(f"Should not generate duplicate code id: {code.code_id}")
                
                self._id2code[code.code_id] = code
                if update_latest_code_id:
                    try:
                        int_code_id = int(code.code_id)
                        self._latest_code_id = max(int_code_id, self._latest_code_id)
                    except:
                        self._latest_code_id += 1

        self.memory.append(item)

    def add(self, item: MemoryItem):
        self._check()
        self._add(item, update_latest_code_id=False)

    def get_memory(self) -> List[MemoryItem]:
        self._check()
        return self.memory
    
    def retrieve(self, query: str) -> List[MemoryItem]:
        self._check()
        keep_n_turns = 4
        chat_history = self.get_memory()
        recent_memory = chat_history[-keep_n_turns:] if len(chat_history) >= keep_n_turns else chat_history
        return recent_memory

    def generate_unique_code_id(self) -> str:
        self._check()
        self._latest_code_id += 1
        return f"{self._latest_code_id}"

    def get_code(self, code_id: str) -> CodeInfo:
        self._check()
        if code_id in self._id2code:
            return self._id2code[code_id]
                
        return None