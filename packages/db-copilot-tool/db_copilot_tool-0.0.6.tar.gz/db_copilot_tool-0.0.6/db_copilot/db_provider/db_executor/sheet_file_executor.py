"""
Script to convert a csv/excel json data into sqlite database
"""
import json
import os
from typing import Dict
import logging
import re
from collections import defaultdict
from datetime import datetime
from functools import lru_cache
from enum import Enum
from io import StringIO

import pandas as pd

from .sqlite_executor import SQLiteExecutor, DatabaseType, TableData


def dependable_import():
    try:
        import recognizers_suite
    except ImportError as e:
        raise ValueError(
            f"Could not import required python package ({e.msg}). Please install dbcopilot with `pip install dbcopilot[extensions] ...` "
        )
    return recognizers_suite


logger = logging.getLogger("sheet_file_executor")


class TextDataType(Enum):
    String = 1
    Number = 2
    Datetime = 3
    Currency = 4
    Percentage = 5


class TableRecognizer:
    def __init__(self) -> None:
        self.sample_num = 3
        self.recognizers_suite = dependable_import()

    @lru_cache(maxsize=1024)
    def _recognize_val_type(self, raw_text: str):
        if self._is_NaN_or_empty(raw_text):
            return None

        text = str(raw_text).strip()

        def have_full(results: list[self.recognizers_suite.ModelResult]):
            return any([x.start == 0 and x.end == len(text) - 1 for x in results])

        date_results = self.recognizers_suite.Recognizers.recognize_datetime(
            text, self.recognizers_suite.Culture.English
        )
        if have_full(date_results):
            return TextDataType.Datetime

        num_results = self.recognizers_suite.Recognizers.recognize_number(
            text, self.recognizers_suite.Culture.English
        )
        if have_full(num_results):
            return TextDataType.Number

        currency_results = self.recognizers_suite.Recognizers.recognize_currency(
            text, self.recognizers_suite.Culture.English
        )
        if have_full(currency_results):
            return TextDataType.Currency

        percentage_results = self.recognizers_suite.Recognizers.recognize_percentage(
            text, self.recognizers_suite.Culture.English
        )
        if have_full(percentage_results):
            return TextDataType.Percentage

        return TextDataType.String

    def _recognize_col_type(self, vals: list):
        val_types = [self._recognize_val_type(v) for v in vals]
        valid_val_types = set([x for x in val_types if x is not None])
        if len(valid_val_types) == 1:
            return list(valid_val_types)[0]

        return TextDataType.String

    def _is_NaN_or_empty(self, val):
        if val is None or pd.isnull(val):
            return True

        if str(val).strip() == "":
            return True

        return False

    def _batch_base_convert(self, vals, recognize_func, postprocess_func):
        spans = []
        batch_input = ""
        for val in vals:
            if batch_input != "":
                batch_input += "|"
            prev_len = len(batch_input)
            if not self._is_NaN_or_empty(val):
                batch_input += str(val).strip()
            spans.append((prev_len, len(batch_input) - 1))

        results = recognize_func(batch_input, self.recognizers_suite.Culture.English)
        all_vals = []
        for span in spans:
            if span[1] < span[0]:
                all_vals.append(pd.NA)
            else:
                full_results = [
                    x for x in results if x.start == span[0] and x.end == span[1]
                ]
                all_vals.append(postprocess_func(full_results[0]))

        return all_vals

    def _convert_number(self, vals):
        return self._batch_base_convert(
            vals,
            self.recognizers_suite.Recognizers.recognize_number,
            lambda x: float(x.resolution["value"]),
        )

    def _convert_currency(self, vals):
        return self._batch_base_convert(
            vals,
            self.recognizers_suite.Recognizers.recognize_currency,
            lambda x: float(x.resolution["value"]),
        )

    def _convert_percentage(self, vals):
        def percent2float(percent_str: str):
            return float(percent_str.rstrip("%")) / 100.0

        return self._batch_base_convert(
            vals,
            self.recognizers_suite.Recognizers.recognize_percentage,
            lambda x: percent2float(x.resolution["value"]),
        )

    def recognize(self, csv_content: str) -> pd.DataFrame:
        if isinstance(csv_content, str):
            csv_stream = StringIO(csv_content)
            df = pd.read_csv(csv_stream)
        elif isinstance(csv_content, list):
            columns = []
            col2freq = defaultdict(int)
            for i, col in enumerate(csv_content[0]):
                if not col.strip():
                    col = "field_{}".format(i + 1)
                freq = col2freq[col]
                if freq > 0:
                    columns.append(col + "_{}".format(freq))
                else:
                    columns.append(col)

                col2freq[col] += 1

            df = pd.DataFrame(
                data=[r for r in csv_content[1:] if len(r) == len(columns)],
                columns=columns,
            )
        else:
            raise NotImplementedError(type(csv_content))

        start_t = datetime.now()

        df = df.dropna(axis="columns", how="all")
        for col in df.keys():
            if df[col].dtype != "object":
                continue
            try:
                vals = [
                    x
                    for x in df[col].values[: self.sample_num]
                    if not self._is_NaN_or_empty(x)
                ]
                col_type = self._recognize_col_type(vals)

                if col_type == TextDataType.Number:
                    df[col] = self._convert_number(df[col].values)
                elif col_type == TextDataType.Currency:
                    df[col] = self._convert_currency(df[col].values)
                elif col_type == TextDataType.Percentage:
                    df[col] = self._convert_percentage(df[col].values)
                # elif col_type == DataType.Datetime:
                #    df[col] = pd.to_datetime(df[col], infer_datetime_format=True)
            except:  # pylint: disable=bare-except
                pass

        logger.info("Table recognize over, cost = {}.".format(datetime.now() - start_t))
        return df


class SheetFileExecutor(SQLiteExecutor):
    """
    DB Executor implementation based on a Excel/Csv file
    """

    def __init__(self, json_data: str, **kwargs) -> None:
        db_path = kwargs.get("db_path", ":memory:")
        super().__init__(db_path, is_local=False, tables=kwargs.get("tables", None))
        self.init_from_json(json_data)

        for table_schema in self.table_schemas.values():
            # Check if primary_key is not already set
            if not table_schema.primary_key:
                table_schema.primary_key = ["row_id"]

    @property
    def db_type(self) -> DatabaseType:
        return DatabaseType.SHEET_FILE

    def init_from_json(self, json_data: str):
        sheet2data: Dict[str, str] = (
            json.loads(json_data) if isinstance(json_data, str) else json_data
        )

        for sheet_name in sheet2data:
            val = sheet2data[sheet_name]
            if isinstance(val, str) and os.path.isfile(val) and val.endswith(".csv"):
                with open(val, encoding="utf-8") as f:
                    sheet2data[sheet_name] = f.read()

        all_table2columns = {}

        table_recognizer = TableRecognizer()
        for sheet_name, sheet_content in sheet2data.items():
            logging.info("Start to recognize for table `{}` ...".format(sheet_name))
            df = table_recognizer.recognize(sheet_content)
            df = clean_and_convert_data_type(df)
            all_table2columns[sheet_name] = [str(x) for x in df.columns]
            df.to_sql(sheet_name, self._conn, if_exists="replace")

        self.table2columns = all_table2columns
        self.get_connection().commit()

    def get_connection(self):
        return self._conn

    def execute_query(self, query: str) -> TableData:
        logging.info("SQL Query: {}".format(query))
        query = self._normalize_sql(query)
        return super().execute_query(query)
    

    def _normalize_sql(self, sql_query) -> str:
        # FIXME: This "normalization" seems unnecessary since column names are already cleansed. Remove if not necessary.
        all_column_names = {c for cols in self.table2columns.values() for c in cols}
        norm_sql_query = None
        try:
            norm_sql_query = self._normalize_sql_new(sql_query, all_column_names)
        except Exception as err:
            # NOTE: This block is added only to ensure backcompatibility in case "_normalize_sql_new" fails. The older function should be deprecated after stabilization.
            logging.warning("Normalize failed. Retrying with older version.")
            norm_sql_query = self._normalize_sql_old(sql_query, all_column_names)
        
        if norm_sql_query != sql_query:
            logging.info("Normalize SQL query over, {} => {}".format(sql_query, norm_sql_query))
        
        return norm_sql_query


    def _normalize_sql_new(self, sql_query, column_names) -> str:
        # Replaces any column names in the query that are preceded or succeeded by one of [" ", ",", "(", ")", "\n"]

        pattern = r"(?<=\s|\(|\)|,|\n)(%s)(?=\s|\(|\)|,|\n)" % "|".join(map(re.escape, column_names))  
        norm_sql_query = re.sub(pattern, r'"\1"', sql_query)  

        return norm_sql_query
    

    def _normalize_sql_old(self, sql_query, column_names) -> str:

        norm_sql_query = sql_query
        for j in range(len(sql_query), -1, -1):
            for i in range(j - 1, -1, -1):
                str_ij = sql_query[i:j]
                if str_ij not in column_names:
                    continue

                if re.match("^[A-Za-z0-9_]+$", str_ij):
                    continue

                if i - 1 <= 0 or sql_query[i - 1] not in [" ", ",", "(", ")", "\n"]:
                    continue

                if j >= len(sql_query) or sql_query[j] not in [
                    " ",
                    ",",
                    "(",
                    ")",
                    "\n",
                ]:
                    continue

                norm_sql_query = (
                    norm_sql_query[:i] + '"{}"'.format(str_ij) + norm_sql_query[j:]
                )

        return norm_sql_query

def clean_and_convert_data_type(df: pd.DataFrame) -> pd.DataFrame:
    df.dropna(how="all", inplace=True)
    name_mappings = convert_column_names(df.columns)
    for column in df.columns:
        df[column] = try_convert_data_type(df[column])

    df.rename(columns=name_mappings, inplace=True)
    df.index.rename("row_id", inplace=True)
    return df


def try_convert_data_type(column: pd.Series) -> pd.Series:
    data_type_converters = [
        lambda x: pd.to_numeric(x, downcast="integer"),
        lambda x: pd.to_numeric(x, downcast="float"),
        lambda x: pd.to_datetime(x, format="ISO8601", infer_datetime_format=True),
    ]

    for converter in data_type_converters:
        try:
            new_column = converter(column)
            logging.info(
                "Convert column `{}` to data type `{}` over!".format(
                    new_column.name, new_column.dtype
                )
            )
            return new_column
        except:  # pylint: disable=bare-except
            pass

    return column


def make_valid_sqlite_column_name(name, existing_names):
    # Convert to lowercase, replace spaces with underscores, and remove invalid characters
    valid_name = re.sub(r"[^a-zA-Z0-9_]", "", name.replace(" ", "_")).lower()

    # Ensure the column name starts with a letter or an underscore
    if not re.match(r"^[a-zA-Z_]", valid_name):
        valid_name = f"_{valid_name}"

    # Append a suffix if the name is not unique, until it becomes unique
    suffix = 1
    original_valid_name = valid_name
    while valid_name in existing_names:
        valid_name = f"{original_valid_name}_{suffix}"
        suffix += 1

    return valid_name


def convert_column_names(names):
    # Keep track of the converted names to ensure uniqueness
    converted_names = set()
    name_mapping = dict()

    for name in names:
        valid_name = make_valid_sqlite_column_name(name, converted_names)
        name_mapping[name] = valid_name
        converted_names.add(valid_name)

    return name_mapping
