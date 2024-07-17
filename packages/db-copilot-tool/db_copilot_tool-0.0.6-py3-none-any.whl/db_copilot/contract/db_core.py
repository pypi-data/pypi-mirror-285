"""
Database contracts definition
"""
from enum import Enum
from typing import List, Tuple
from dataclasses import dataclass

from .generic import DictMixin, PromptMixin, get_field_names
from .data_core import TableData, _DEFAULT_TABULATE
from .knowledge_core import KnowledgePiece

_MAX_TRUNCATE_LENGTH = 100


def _default_truncate_long(value):
    if not isinstance(value, str):
        return value

    if len(value) >= _MAX_TRUNCATE_LENGTH:
        return value[:_MAX_TRUNCATE_LENGTH] + "..."

    return value


class DatabaseType(str, Enum):
    """
    Database type definition
    """

    SQLITE = "sqlite"
    SQLSERVER = "sqlserver"
    SHEET_FILE = "sheet_file"
    CLICKHOUSE = "clickhouse"
    KUSTO = "kusto"

    # limited support
    COSMOS = "cosmos"

    # Not supported yet
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    OTHER = "other"


class SQLDialect(str, Enum):
    """
    SQL dialect definition
    """

    DEFAULT_SQL = "sql"
    SQLITE = "sqlite"
    TSQL = "tsql"
    CLICKHOUSE = "clickhouse"
    KQL = "kql"

    def bracket_field_name(self, name: str) -> str:
        """
        Bracket the name of name in SQL to ensure no ambiguity
        """
        if name is None:
            return None

        if isinstance(name, str):
            if self.value == SQLDialect.KQL:
                if name.startswith("['") and name.endswith("']"):
                    return name
                return "['{}']".format(name)

            if self.value == SQLDialect.CLICKHOUSE:
                return f"{name}"

            if name.startswith("[") and name.endswith("]"):
                return name

            return f"[{name}]"

        assert isinstance(
            name, (list, tuple)
        ), f"Name must be a str or a list of str: {name}/{type(name)}"
        return ".".join(map(self.bracket_field_name, name))

    @classmethod
    def from_db_type(cls, db_type: DatabaseType) -> "SQLDialect":
        """
        Init sql dialect from the database type
        """
        return {
            DatabaseType.SQLITE: SQLDialect.SQLITE,
            DatabaseType.SHEET_FILE: SQLDialect.SQLITE,
            DatabaseType.SQLSERVER: SQLDialect.TSQL,
            DatabaseType.CLICKHOUSE: SQLDialect.CLICKHOUSE,
            DatabaseType.KUSTO: SQLDialect.KQL,
        }.get(db_type, SQLDialect.DEFAULT_SQL)


class ColumnSecurityLevel(int, Enum):
    NORMAL = 0
    PROTECTED = 1  # Values will not be used for grounding and prompt building
    CONFIDENTIAL = 2  # Can't fetch values in SQL query, only limited aggregation functions are allowed.


@dataclass
class ColumnSchema(DictMixin):
    """
    Column schema definition
    """

    name: str
    data_type: str
    description: str = None
    security_level: ColumnSecurityLevel = ColumnSecurityLevel.NORMAL


@dataclass
class TableSchema(DictMixin):
    """
    Schema definition of a table
    """

    name: str
    columns: List[ColumnSchema]
    num_rows: int
    primary_key: List[str]  # List of primary key columns
    foreign_keys: List[Tuple[str, str, str]]
    description: str = None

    def __str__(self) -> str:
        columns = [
            f"  {column.name} {column.data_type}"
            if column.name not in self.foreign_keys
            else f"{column.name} {column.data_type} PRIMARY KEY".format()
            for column in self.columns
        ]

        for fk_col, ref_tbl, ref_col in self.foreign_keys:
            columns.append(f"  <FOREIGN_KEY>({fk_col}) REFERENCES {ref_tbl}({ref_col})")

        return "Table {}(\n{}\n)".format(self.name, ",\n".join(columns))

    @property
    def num_rows_str(self) -> str:
        return str(self.num_rows) if self.num_rows >= 0 else "unkown"

    @property
    def foreign_columns(self) -> List[str]:
        """
        Column names in foreign keys
        """
        return [x[0] for x in self.foreign_keys]

    @property
    def referenced_tables(self) -> List[str]:
        """
        Referenced table names of foreign keys
        """
        return [x[1] for x in self.foreign_keys]

    @classmethod
    def from_dict(cls, obj) -> "TableSchema":
        obj["columns"] = [ColumnSchema.from_dict(x) for x in obj["columns"]]
        return super().from_dict(obj)

    def lookup_column_schema(self, column_name: str) -> ColumnSchema:
        """
        Lookup the column schema when given a column name
        """
        for column_schema in self.columns:
            if column_name == column_schema.name:
                return column_schema
        raise ValueError(f"Column `{column_name}` is not found.")


@dataclass
class TableSnapshot(DictMixin, PromptMixin):
    """
    Snapshot definition, used as the result of grounding module.
    It should be a sub-view of a table on the database with limited columns and rows.
    """

    schema: TableSchema
    data_frame: TableData

    @classmethod
    def from_dict(cls, obj: dict) -> "TableSnapshot":
        obj["schema"] = TableSchema.from_dict(obj["schema"])
        obj["data_frame"] = TableData.from_dict(obj["data_frame"])
        return super().from_dict(obj)

    def as_prompt_text(self, **kwargs) -> str:
        dialect = kwargs.get("sql_dialect", SQLDialect.DEFAULT_SQL)
        field_func = dialect.bracket_field_name
        prompt_string = f"Table {field_func(self.schema.name)} with {self.schema.num_rows_str} rows in total"
        if self.schema.description and kwargs.get("add_table_description", True):
            prompt_string += ", " + self.schema.description.strip()

        # Add table content
        column_schemas = [
            self.schema.lookup_column_schema(col) for col in self.data_frame.columns
        ]
        displayed_headers = [
            f"{col_schema.name} ({col_schema.data_type})"
            if kwargs.get("add_data_type", True)
            else col_schema.name
            for col_schema in column_schemas
        ]

        tabulate_func = kwargs.get("tabulate_func", _DEFAULT_TABULATE)
        assert (
            tabulate_func is not None
        ), "Please run `pip install tabulate` to enable default tabulate"

        # truncate long cell
        data = self.data_frame.data
        if kwargs.get("truncate_long_text", True):
            truncate_long_func = kwargs.get(
                "truncate_long_func", _default_truncate_long
            )
            data = [[truncate_long_func(val) for val in row] for row in data]

        prompt_string += ":\n" + tabulate_func(data, displayed_headers)

        # Add primary key
        if kwargs.get("add_primary_key", True) and self.schema.primary_key:
            primary_key_string = ", ".join(
                [field_func(c) for c in self.schema.primary_key]
            )
            prompt_string += f"\nPRIMARY KEY ({primary_key_string})"

        # Add foreign keys
        if kwargs.get("add_foreign_keys", True):
            for fk_column, ref_table, ref_col in self.schema.foreign_keys:
                prompt_string += f"\n<FOREIGN_KEY> {field_func(fk_column)} REFERENCES {field_func(ref_table)}({field_func(ref_col)})"

        if kwargs.get("add_column_description", True):
            column_decs = [
                f"- {field_func(column.name)}: {column.description}"
                for column in column_schemas
                if column.description
            ]

            column_decs = "\n".join(column_decs)
            if column_decs:
                prompt_string += (
                    f"\nHere list the descriptions of columns:\n{column_decs}"
                )

        return prompt_string

    def as_prompt_text_compact(self, **kwargs) -> str:
        dialect = kwargs.get("sql_dialect", SQLDialect.DEFAULT_SQL)
        field_func = dialect.bracket_field_name
        prompt_string = f"Table {field_func(self.schema.name)} with {self.schema.num_rows_str} rows in total"
        if self.schema.description and kwargs.get("add_table_description", True):
            prompt_string += ", " + self.schema.description.strip()

        # Add table content
        column_schemas = [
            self.schema.lookup_column_schema(col) for col in self.data_frame.columns
        ]
        displayed_headers = [
            f"{field_func(col_schema.name)} ({col_schema.data_type})"
            if kwargs.get("add_data_type", True)
            else col_schema.name
            for col_schema in column_schemas
        ]

        tabulate_func = kwargs.get("tabulate_func", _DEFAULT_TABULATE)
        assert (
            tabulate_func is not None
        ), "Please run `pip install tabulate` to enable default tabulate"

        # truncate long cell
        data = self.data_frame.data
        if kwargs.get("truncate_long_text", True):
            truncate_long_func = kwargs.get(
                "truncate_long_func", _default_truncate_long
            )
            data = [[truncate_long_func(val) for val in row] for row in data]

        if kwargs.get("add_data_type", True):
            prompt_string += (
                ':\nColumns (format: "{ColumnName} ({ColumnType})"): '
                + " | ".join(displayed_headers)
            )
        else:
            prompt_string += ":\nColumns: " + " | ".join(displayed_headers)

        prompt_string += "\nSampled rows:\n"
        for row in data:
            row = [str(value) for value in row]
            prompt_string += " | ".join(row) + "\n"
        prompt_string = prompt_string.strip()

        # Add primary key
        if kwargs.get("add_primary_key", True) and self.schema.primary_key:
            primary_key_string = ", ".join(
                [field_func(c) for c in self.schema.primary_key]
            )
            prompt_string += f"\nPRIMARY KEY ({primary_key_string})"

        # Add foreign keys
        if kwargs.get("add_foreign_keys", True):
            for fk_column, ref_table, ref_col in self.schema.foreign_keys:
                prompt_string += f"\n<FOREIGN_KEY> {field_func(fk_column)} REFERENCES {field_func(ref_table)}({field_func(ref_col)})"

        if kwargs.get("add_column_description", True):
            column_decs = [
                f"- {field_func(column.name)}: {column.description}"
                for column in column_schemas
                if column.description
            ]

            column_decs = "\n".join(column_decs)
            if column_decs:
                prompt_string += (
                    f"\nHere list the descriptions of columns:\n{column_decs}"
                )

        return prompt_string


@dataclass
class DBSnapshot(DictMixin, PromptMixin):
    """
    Retrieved database snapshot definition
    """

    db_type: DatabaseType
    table_snapshots: List[TableSnapshot]
    knowledge_pieces: List[KnowledgePiece] = None

    @classmethod
    def from_dict(cls, obj: dict) -> "DBSnapshot":
        obj["db_type"] = DatabaseType(obj["db_type"])
        obj["table_snapshots"] = [
            TableSnapshot.from_dict(x) for x in obj["table_snapshots"]
        ]
        obj["knowledge_pieces"] = (
            [KnowledgePiece.from_dict(x) for x in obj["knowledge_pieces"]]
            if obj.get("knowledge_pieces", None)
            else None
        )
        return cls(**{k: v for k, v in obj.items() if k in get_field_names(cls)})

    def as_prompt_text(self, **kwargs) -> str:
        sql_dialect = SQLDialect.from_db_type(self.db_type)
        prompt_text = (
            f"The {self.db_type.value} database contains {len(self.table_snapshots)} tables:\n"
            if not kwargs.get("prefix", None)
            else kwargs.pop("prefix")
        )

        tbl_prompt_strs = [
            col_snapshot.as_prompt_text_compact(sql_dialect=sql_dialect, **kwargs)
            for col_snapshot in self.table_snapshots
        ]

        prompt_text += "\n\n".join(tbl_prompt_strs)

        if kwargs.get("add_knowledge", True) and self.knowledge_pieces:
            knowledge_prefix = "The relevant knowledge on the database is listed below to help you answer the question:"
            knowledge_body = [
                f"- {x.as_prompt_text(**kwargs)}"
                for x in self.knowledge_pieces
            ]

            prompt_text += "\n\n{}\n{}".format(
                knowledge_prefix, "\n".join(knowledge_body)
            )

        return prompt_text
