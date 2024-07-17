from typing import List
import json
import time
from datetime import datetime
from functools import wraps
import logging


class StopWatcher:
    def __init__(self) -> None:
        self.start = datetime.now()
    
    def elapsed_ms(self, reset: bool=False) -> int:
        cost = (datetime.now() - self.start).total_seconds() * 1000

        if reset:
            self.reset()

        return int(cost)
    
    def reset(self):
        self.start = datetime.now()


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        logging.info(f'Call function ``{func.__qualname__}`` ``{args[1:]}`` cost ``{total_time:.3f}``s.')
        return result
    return timeit_wrapper

def argsort(array: List[float], descending=True):
    sorted_indices = list(sorted(range(len(array)), key=lambda i: array[i], reverse=descending))
    return sorted_indices


def load_json_object(path: str):
    with open(path, 'r', encoding='utf-8') as fr:
        return json.load(fr)

def distinct_list(vals: List) -> List:
    unique_vals = []
    for val in vals:
        if val in unique_vals:
            continue
    
        unique_vals.append(val)

    return unique_vals