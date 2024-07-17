"""
Contracts for basic data objects
"""
from collections import abc
from datetime import date, datetime, time
from decimal import Decimal
from dataclasses import dataclass
import json
import logging
from typing import List

import numpy as np
import pandas as pd

from .generic import DictMixin, PromptMixin

logger = logging.getLogger("data_core")

try:
    from tabulate import tabulate
    def _tabulate_psql(data, headers) -> str:
        return tabulate(data, headers, tablefmt="psql")
    _DEFAULT_TABULATE = _tabulate_psql
except: # pylint: disable=bare-except
    _DEFAULT_TABULATE = None


class TypedValueConverter:
    """
    Static class defined for type-value serialization and deserialization
    """
    converters: dict = {
        'none': None,
        'int': (lambda s: None if np.isnan(s) else int(s), lambda s: s),
        'long': (lambda s: None if np.isnan(s) else int(s), lambda s: s),
        'float': (float, lambda s: s),
        'real': (float, lambda s: s),
        'double': (float, lambda s: s),
        'str': (str, lambda s: s),
        'string': (str, lambda s: s),
        'date': (lambda x: x.isoformat() if x != 'NaT' else 'NaT', lambda s: pd.Timestamp(s).to_pydatetime() if s != 'NaT' else 'NaT'),
        'datetime': (lambda x: x.isoformat() if x != 'NaT' else 'NaT', lambda s: pd.Timestamp(s).to_pydatetime() if s != 'NaT' else 'NaT'),
        'time': (lambda x: str(x) if x != 'NaT' else 'NaT', lambda s: pd.Timedelta(s).to_pytimedelta() if s != 'NaT' else 'NaT'),
        'timespan': (lambda x: str(x) if x != 'NaT' else 'NaT', lambda s: pd.Timedelta(s).to_pytimedelta() if s != 'NaT' else 'NaT'),
        'decimal': (str, Decimal),
        'array': (str, lambda s: s),
        'dict': (str, lambda s: s),
        'dynamic': (json.dumps, json.loads),
        'guid': (str, lambda s: s),
        'bool': (bool, lambda s: s),
        'boolean': (bool, lambda s: s),
    }

    @staticmethod
    def register(data_type: str, serialize_func: abc.Callable, deserialize_func: abc.Callable):
        """
        Register or update a serialize and deserialize function for a data type
        """
        assert serialize_func is not None and deserialize_func is not None
        TypedValueConverter.converters[data_type] = (serialize_func, deserialize_func)

    @staticmethod
    def serialize(data_type: str, value: object, default_type: str=None) -> object:
        """
        Serialize a typed-value into json basic object
        """
        if pd.isnull(value):
            return None

        data_type = data_type.lower()
        if data_type not in TypedValueConverter.converters:
            if default_type:
                data_type = default_type
            else:
                raise NotImplementedError(f"Data type `{data_type}`")

        converter = TypedValueConverter.converters[data_type]
        try:
            return converter[0](value)
        except:
            return str(value)

    @staticmethod
    def deserialize(data_type: str, value: object, default_type: str=None) -> object:
        """
        Deserialize a typed value from json basic object
        """
        if value is None:
            return value

        data_type = data_type.lower()
        if data_type not in TypedValueConverter.converters:
            if default_type:
                data_type = default_type
            else:
                raise NotImplementedError(f"Data type `{data_type}`")

        converter = TypedValueConverter.converters[data_type]
        if converter is None:
            return value

        try:
            return converter[1](value)
        except:
            return value

_TABLE_DATA_EMPTY_COLUMN = "_empty"
_TABLE_DATA_EMPTY_COLUMN_TYPE = 'str'

@dataclass
class TableData(DictMixin, PromptMixin):
    """
    Tabular data
    """
    columns: List[str]
    column_types: List[str]
    data: List[List[object]]
    caption: str = None # The description of the table

    
    def _no_column_info(self) -> bool:
        return len(self.columns) == 1 and self.columns[0] == _TABLE_DATA_EMPTY_COLUMN

    @classmethod
    def empty_column_info_name(cls) -> str:
        return _TABLE_DATA_EMPTY_COLUMN
    @classmethod
    def empty_column_info_type(cls) -> str:
        return _TABLE_DATA_EMPTY_COLUMN_TYPE

    @property
    def num_rows(self) -> int:
        return len(self.data)

    def to_dict(self) -> dict:
        obj = {
            "columns": self.columns,
            "column_types": self.column_types
        }

        obj["data"] = [
            [TypedValueConverter.serialize(d_type, v) for v, d_type in zip(row, self.column_types)]
            for row in self.data
        ]

        if self.caption:
            obj["caption"] = self.caption

        return obj

    def as_prompt_text(self, **kwargs) -> str:
        sample_rows = self.data if len(self.data) <= 3 else self.data[:3]
        if self._no_column_info():
            headers_str = ""
        else:
            headers_str = f"""
The headers are: {' | '.join([(self.columns[i] + "(data_type=" + self.column_types[i] + ")") for i in range(len(self.columns))])}
""".lstrip()
        return f"""
The result contains {len(self.data)} rows.
{headers_str}Sample rows: {str(sample_rows)}
""".strip()

    @classmethod
    def from_dict(cls, obj: dict) -> "TableData":
        obj["data"] = [
            [TypedValueConverter.deserialize(d_type, v)
            for v, d_type in zip(row, obj["column_types"])]
            for row in obj["data"]
        ]

        return super().from_dict(obj)

    @classmethod
    def from_df(cls, df: pd.DataFrame) -> "TableData":
        columns = list(df.columns)
        dtype_map = {
            "int64": "int",
            "int32": "int",
            "float64": "float",
            "datetime64[ns]": "datetime",
            "object": "str",
        }
        column_types = list(map(lambda dt: f"{dt}", df.dtypes))
        column_types = list(map(lambda dt: dt if dt not in dtype_map else dtype_map[dt], column_types))
        data = []
        for _, row in df.iterrows():
            r = []
            for c in columns:
                r.append(row[c])
            data.append(r)
        return TableData(data=data, column_types=column_types, columns=columns)

    def rows(self, as_dict: bool=True) -> abc.Iterator:
        for row in self.data:
            if as_dict:
                yield dict(zip(self.columns, row))
            else:
                yield tuple(row)

    def __getitem__(self, column: str) -> list:
        column2indices = { col: i for i, col in enumerate(self.columns) }
        if column not in column2indices:
            raise KeyError(f"Column `{column}` not found.")
    
        column_idx = column2indices[column]
        return [row[column_idx] for row in self.data]
