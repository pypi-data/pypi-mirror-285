from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, TypedDict

import pandas as pd


class Value(TypedDict):
    kind: Dict[str, Any]


class SqlResultRowResponse(TypedDict):
    value: Dict[str, Value]


@dataclass
class SqlResultResponse:
    headers: List[str]
    rows: List[SqlResultRowResponse]


def convert_sql_response(
    response: SqlResultResponse,
) -> pd.DataFrame:
    fields = response.headers

    def parse_value(case_type, value):
        if case_type == "nullValue":
            return None
        elif case_type == "doubleValue":
            return value[case_type]
        elif case_type == "floatValue":
            return value[case_type]
        elif case_type == "int32Value":
            return value[case_type]
        elif case_type == "int64Value":
            return int(value[case_type])
        elif case_type == "uint32Value":
            return value[case_type]
        elif case_type == "uint64Value":
            return int(value[case_type])
        elif case_type == "sint32Value":
            return value[case_type]
        elif case_type == "sint64Value":
            return int(value[case_type])
        elif case_type == "fixed32Value":
            return value[case_type]
        elif case_type == "fixed64Value":
            return int(value[case_type])
        elif case_type == "sfixed32Value":
            return value[case_type]
        elif case_type == "sfixed64Value":
            return int(value[case_type])
        elif case_type == "boolValue":
            return value[case_type]
        elif case_type == "stringValue":
            return value[case_type]
        elif case_type == "bytesValue":
            return value[case_type]
        elif case_type == "structValue":
            return value[case_type]["fields"]
        elif case_type == "listValue":
            rows = []
            for v in value[case_type]["values"]:
                rows.append(parse_value(v["kind"]["$case"], v["kind"]))
            return rows

    parsed_rows = []
    for row in response.rows:
        parsed_row = {}
        for field in fields:
            value = row["value"][field]["kind"]
            case_type = value["$case"]
            parsed_row[field] = parse_value(case_type, value)
        parsed_rows.append(parsed_row)
    return pd.DataFrame.from_dict(parsed_rows)  # type: ignore
