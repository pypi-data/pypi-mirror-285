from typing import Dict, Optional

import pandas as pd
from pandas import DataFrame
from pandas.core.dtypes.common import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_string_dtype,
)


class SQLUtils:
    def __init__(
        self,
        dataframe: DataFrame,
        table_name: str,
        column_types: Optional[Dict[str, str]] = None,
    ):
        self.dataframe: DataFrame = dataframe
        self.table_name: str = table_name
        self.column_types = column_types or {}

    def generate_create_table_sql(self) -> str:
        """Generate a CREATE TABLE SQL statement based on the DataFrame schema."""
        columns: list[str] = []
        for col_name, dtype in self.dataframe.dtypes.items():
            if col_name in self.column_types.items():
                column_type = self.column_types[str(col_name)]
                column_sql = f"{col_name} {column_type}"
            elif is_integer_dtype(dtype):
                column_sql = f"{col_name} INTEGER"
            elif is_float_dtype(dtype):
                column_sql = f"{col_name} REAL"
            elif is_bool_dtype(dtype):
                column_sql = f"{col_name} BOOLEAN"
            elif is_datetime64_any_dtype(dtype):
                column_sql = f"{col_name} TIMESTAMP"
            elif is_string_dtype(dtype):
                column_sql = f"{col_name} TEXT"
            else:
                column_sql = f"{col_name} TEXT"  # Default to TEXT if type is unknown
            columns.append(column_sql)
        columns_sql: str = ",\n  ".join(columns)
        return f"CREATE TABLE {self.table_name} (\n  {columns_sql}\n);"

    def generate_insert_sql(self) -> str:
        """Generate INSERT INTO SQL statements for each row in the DataFrame."""
        insert_sql: str = f"INSERT INTO {self.table_name} ({', '.join(self.dataframe.columns)}) VALUES "
        rows: list[str] = []
        for _, row in self.dataframe.iterrows():
            values: list[str] = []
            for item in row:
                if isinstance(item, str):
                    escaped_item = item.replace("'", "''")
                    value = f"'{escaped_item}'"
                elif isinstance(item, bool):
                    value = str(item).upper()
                elif isinstance(item, (int, float)):
                    value = str(item)
                elif isinstance(item, list):
                    value = f"ARRAY{item}"
                elif pd.api.types.is_datetime64_any_dtype(item):
                    value = f"'{item.isoformat()}'"
                elif pd.isna(item):
                    value = "NULL"
                else:
                    value = f"'{str(item)}'"
                values.append(value)
            row_sql: str = f"({', '.join(values)})"
            rows.append(row_sql)
        all_rows_sql: str = ",\n".join(rows)
        return f"{insert_sql}\n{all_rows_sql};"

    def generate_update_sql(self, key_columns: list[str]) -> str:
        """Generate a single UPDATE SQL statement using CASE for each row in the DataFrame."""
        if not all(key in self.dataframe.columns for key in key_columns):
            raise ValueError("All key columns must be present in the DataFrame.")

        set_clauses: list[str] = []
        for col in self.dataframe.columns:
            if col not in key_columns:
                cases: list[str] = []
                for _, row in self.dataframe.iterrows():
                    key_conditions = " AND ".join(
                        f"{key} = {self._format_value(row[key])}" for key in key_columns
                    )
                    cases.append(
                        f"WHEN {key_conditions} THEN {self._format_value(row[col])}"
                    )
                set_clauses.append(f"{col} = CASE {' '.join(cases)} ELSE {col} END")

        return f"UPDATE {self.table_name} SET {', '.join(set_clauses)};"

    def generate_replace_sql(self) -> dict[str, str]:
        """Generate a CREATE OR REPLACE TABLE SQL statement and INSERT INTO SQL statements."""
        drop_table_sql: str = f"DROP TABLE IF EXISTS {self.table_name};"
        create_table_sql: str = self.generate_create_table_sql()
        insert_sql: str = self.generate_insert_sql()
        return {
            "drop_table_sql": drop_table_sql,
            "create_table_sql": create_table_sql,
            "insert_sql": insert_sql,
        }

    def _format_value(self, value):
        """Format the value for SQL queries."""
        if pd.isna(value):
            return "NULL"
        elif isinstance(value, str):
            escaped_value = value.replace("'", "''")
            return f"'{escaped_value}'"
        elif isinstance(value, bool):
            return str(value).upper()
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, list):
            return f"ARRAY{value}"
        elif pd.api.types.is_datetime64_any_dtype(value):
            return f"'{value.isoformat()}'"
        else:
            return f"'{str(value)}'"
