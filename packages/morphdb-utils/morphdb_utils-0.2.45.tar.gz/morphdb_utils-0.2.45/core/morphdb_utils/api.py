from __future__ import annotations

import glob
import io
import os
import urllib.parse
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

import pandas as pd
import requests
import urllib3
from morphdb_utils.type import (
    ListStorageDirectoryResponse,
    LoadDataParams,
    MorphApiError,
    RefResponse,
    SignedUrlResponse,
)
from morphdb_utils.utils.response import (
    convert_filepath_to_df,
    convert_signed_url_response_to_dataframe,
    handle_morph_response,
)
from morphdb_utils.utils.sql import SQLUtils
from pandas import DataFrame
from requests.exceptions import Timeout
from urllib3.exceptions import InsecureRequestWarning

from morph.task.utils.morph import MorphYaml
from morph.task.utils.os import OsUtils
from morph.task.utils.sqlite import SqliteDBManager

urllib3.disable_warnings(InsecureRequestWarning)


@dataclass
class EnvVars:
    database_id: str
    base_url: str
    team_slug: str
    api_key: str
    canvas: Optional[str] = None


# ===============================================
#
# Implementation
#
# ===============================================
def _canonicalize_base_url(base_url: str) -> str:
    if base_url.startswith("http"):
        return base_url
    else:
        return f"https://{base_url}"


def _read_configuration_from_env() -> EnvVars:
    """
    Read configuration from environment variables
    These variables are loaded from ini file when the morph run command is executed
    """
    database_id_value = os.getenv("MORPH_DATABASE_ID")
    base_url_value = os.getenv("MORPH_BASE_URL")
    team_slug_value = os.getenv("MORPH_TEAM_SLUG")
    api_key_value = os.getenv("MORPH_API_KEY")
    canvas_value = os.getenv("MORPH_CANVAS")

    if not database_id_value:
        raise MorphApiError("Internal error: database_id is not set")
    if not base_url_value:
        raise MorphApiError("Internal error: base_url is not set")
    if not team_slug_value:
        raise MorphApiError("Internal error: team_slug is not set")
    if not api_key_value:
        raise MorphApiError("Internal error: api_key is not set")

    return EnvVars(
        database_id=database_id_value,
        base_url=base_url_value,
        team_slug=team_slug_value,
        api_key=api_key_value,
        canvas=canvas_value,
    )


def __execute_sql_impl(
    sql: str,
    connection_slug: str | None = None,
) -> pd.DataFrame:
    config_from_env = _read_configuration_from_env()
    database_id = config_from_env.database_id
    base_url = config_from_env.base_url
    team_slug = config_from_env.team_slug
    api_key = config_from_env.api_key

    headers = {
        "teamSlug": team_slug,
        "X-Api-Key": api_key,
    }

    split_url = urllib.parse.urlsplit(base_url)
    url_sql = urllib.parse.urljoin(
        _canonicalize_base_url(base_url),
        f"{split_url.path}/{database_id}/sql/csv",
    )

    request = {"sql": sql}
    if connection_slug is not None:
        request["connectionSlug"] = connection_slug

    try:
        response = requests.post(url_sql, headers=headers, json=request, verify=True)
    except Timeout:
        raise MorphApiError("Process Timeout while executing SQL")
    except Exception as e:
        raise MorphApiError(f"SQL error: {e}")

    response_body = handle_morph_response(response)
    try:
        structured_response_body = SignedUrlResponse(url=response_body["url"])
        download_url = requests.get(structured_response_body.url)
    except Exception as e:
        raise MorphApiError(f"{e}")

    try:
        if not download_url.content:
            return pd.DataFrame()

        chunks = []
        for chunk in pd.read_csv(
            io.BytesIO(download_url.content),
            header=0,
            chunksize=1_000_000,
            encoding_errors="replace",
        ):
            chunks.append(chunk)
        df: DataFrame = pd.concat(chunks, axis=0)
        return df
    except Exception as e:
        raise MorphApiError(f"{e}")


def __get_data_path_impl(
    filepath: str,
    specific_dirpath: str | None = None,
    specific_filepath: str | None = None,
) -> str | None:
    config_from_env = _read_configuration_from_env()
    database_id = config_from_env.database_id
    team_slug = config_from_env.team_slug

    project_root = MorphYaml.find_abs_project_root_dir()
    db_manager = SqliteDBManager(project_root)

    resource = MorphYaml.find_resource_by_path(filepath, project_root, db_manager)
    if not resource:
        raise MorphApiError(f"Reference cell {filepath} not found")

    cell_type = MorphYaml.get_cell_type(resource.path)

    if cell_type == "file":
        if specific_dirpath is not None:
            abs_dir_path = os.path.abspath(specific_dirpath)
            if specific_filepath is not None:
                abs_specific_filepath = os.path.abspath(specific_filepath)
                if os.path.exists(abs_specific_filepath):
                    return abs_specific_filepath
                storage_path = _get_pre_signed_url_path(
                    abs_specific_filepath, team_slug, database_id
                )
                return __get_presigned_url(storage_path)
            if os.path.exists(abs_dir_path):
                latest_filepath = __get_latest_file(abs_dir_path)
                if latest_filepath is not None:
                    return latest_filepath
                storage_data = __list_storage_dirs(abs_dir_path)
                if storage_data is not None and len(storage_data.files) > 0:
                    storage_path = _get_pre_signed_url_path(
                        storage_data.files[0].path, team_slug, database_id
                    )
                    return __get_presigned_url(storage_path)
            return None
        abs_file_path = os.path.abspath(filepath)
        if os.path.exists(abs_file_path):
            return abs_file_path
        return None
    elif cell_type == "directory":
        abs_dir_path = os.path.abspath(filepath)
        if specific_filepath is not None:
            abs_specific_filepath = os.path.abspath(specific_filepath)
            if os.path.exists(abs_specific_filepath):
                return abs_specific_filepath
            storage_path = _get_pre_signed_url_path(
                abs_specific_filepath, team_slug, database_id
            )
            return __get_presigned_url(storage_path)
        if os.path.exists(abs_dir_path):
            latest_filepath = __get_latest_file(abs_dir_path)
            if latest_filepath is not None:
                return latest_filepath
            storage_data = __list_storage_dirs(abs_dir_path)
            if storage_data is not None and len(storage_data.files) > 0:
                storage_path = _get_pre_signed_url_path(
                    storage_data.files[0].path, team_slug, database_id
                )
                return __get_presigned_url(storage_path)
        return None
    else:
        if specific_dirpath is not None:
            abs_dir_path = os.path.abspath(specific_dirpath)
            if specific_filepath is not None:
                abs_specific_filepath = os.path.abspath(specific_filepath)
                if os.path.exists(abs_specific_filepath):
                    return abs_specific_filepath
                storage_path = _get_pre_signed_url_path(
                    abs_specific_filepath, team_slug, database_id
                )
                return __get_presigned_url(storage_path)
            if os.path.exists(abs_dir_path):
                latest_filepath = __get_latest_file(abs_dir_path)
                if latest_filepath is not None:
                    return latest_filepath
                storage_data = __list_storage_dirs(abs_dir_path)
                if storage_data is not None and len(storage_data.files) > 0:
                    storage_path = _get_pre_signed_url_path(
                        storage_data.files[0].path, team_slug, database_id
                    )
                    return __get_presigned_url(storage_path)
            return None
        else:
            abs_file_path = os.path.abspath(filepath)
            if specific_filepath is not None:
                abs_specific_filepath = os.path.abspath(specific_filepath)
                if os.path.exists(abs_specific_filepath):
                    return abs_specific_filepath
                storage_path = _get_pre_signed_url_path(
                    abs_specific_filepath, team_slug, database_id
                )
                return __get_presigned_url(storage_path)
            abs_dir_path = resource.output_paths[0] if resource.output_paths else None  # type: ignore
            if abs_dir_path.endswith("{ext()}"):
                abs_dir_path = os.path.dirname(abs_dir_path)
            if os.path.exists(abs_dir_path):
                latest_filepath = __get_latest_file(abs_dir_path)
                if latest_filepath is not None:
                    return latest_filepath
                storage_data = __list_storage_dirs(abs_dir_path)
                if storage_data is not None and len(storage_data.files) > 0:
                    storage_path = _get_pre_signed_url_path(
                        storage_data.files[0].path, team_slug, database_id
                    )
                    return __get_presigned_url(storage_path)
            return None


def __get_file_impl(
    filepath: str,
) -> str:
    config_from_env = _read_configuration_from_env()
    database_id = config_from_env.database_id
    team_slug = config_from_env.team_slug

    expanded_filepath = os.path.expanduser(filepath)
    abs_path = OsUtils.normalize_path(
        expanded_filepath, MorphYaml.find_abs_project_root_dir()
    )
    if os.path.exists(abs_path):
        return abs_path

    storage_path = _get_pre_signed_url_path(abs_path, team_slug, database_id)
    return __get_presigned_url(storage_path)


# ===============================================
#
# Utils
#
# ===============================================
def __get_presigned_url(storage_path: str) -> str:
    config_from_env = _read_configuration_from_env()
    base_url = config_from_env.base_url
    team_slug = config_from_env.team_slug
    api_key = config_from_env.api_key

    headers = {
        "teamSlug": team_slug,
        "X-Api-Key": api_key,
    }

    split_url = urllib.parse.urlsplit(base_url)
    request_url = urllib.parse.urljoin(
        _canonicalize_base_url(base_url),
        f"{split_url.path}/resource/morph-storage/download-url",
    )

    query_params = {
        "filename": storage_path,
    }

    request_url += f"?{urllib.parse.urlencode(query_params)}"

    try:
        response = requests.get(request_url, headers=headers)
    except Timeout:
        raise MorphApiError("Process Timeout while executing get url")
    except Exception as e:
        raise MorphApiError(f"{e}")

    response_body = handle_morph_response(response)
    if "preSignedDownloadUrl" not in response_body:
        raise MorphApiError("preSignedDownloadUrl is not in response body")
    if not response_body["preSignedDownloadUrl"]:
        raise MorphApiError("preSignedDownloadUrl is empty")
    if not isinstance(response_body["preSignedDownloadUrl"], str):
        raise MorphApiError("preSignedDownloadUrl is invalid")
    return response_body["preSignedDownloadUrl"]


def __get_latest_file(abs_path: str) -> str | None:
    if os.path.isfile(abs_path):
        return abs_path

    files = glob.glob(os.path.join(abs_path, "*"))

    if not files:
        return None

    latest_file = max(files, key=os.path.getmtime)

    return latest_file


def __list_storage_dirs(
    prefix: str,
    depth: int = 2,
) -> ListStorageDirectoryResponse | None:
    config_from_env = _read_configuration_from_env()
    database_id = config_from_env.database_id
    base_url = config_from_env.base_url
    api_key = config_from_env.api_key

    headers = {
        "X-Api-Key": api_key,
    }

    split_url = urllib.parse.urlsplit(base_url)
    request_url = urllib.parse.urljoin(
        _canonicalize_base_url(base_url),
        f"{split_url.path}/resource/morph-storage/directory",
    )

    query_params = {
        "databaseId": database_id,
        "depth": depth,
        "path": prefix,
    }
    request_url += f"?{urllib.parse.urlencode(query_params)}"

    try:
        response = requests.get(request_url, headers=headers)
    except Timeout:
        raise MorphApiError("Process Timeout while executing list_storage_dirs")
    except Exception as e:
        raise MorphApiError(f"{e}")

    response_body = handle_morph_response(response)

    try:
        return ListStorageDirectoryResponse(**response_body)
    except Exception as e:
        raise MorphApiError(f"list_storage_dirs error: {e}")


def __process_records(
    action: str,
    *args: Union[RefResponse, pd.DataFrame],
    **kwargs: Union[str, int, bool, List[str], Dict[str, str]],
) -> None:
    # Validate action
    if action not in {"create", "insert", "update"}:
        raise MorphApiError(
            "Invalid action provided. Must be 'create', 'insert', or 'update'."
        )

    # Validate *args
    if not args or (
        not isinstance(args[0], RefResponse) and not isinstance(args[0], pd.DataFrame)
    ):
        raise MorphApiError(
            "Invalid *args provided: RefResponse or pd.DataFrame is required."
        )

    # Validate **kwargs
    if "table_name" not in kwargs:
        raise MorphApiError("Invalid **kwargs provided: 'table_name' is required.")
    table_name_value = kwargs.pop("table_name")
    if not isinstance(table_name_value, str):
        raise MorphApiError("Invalid **kwargs provided: 'table_name' must be a string.")
    table_name: str = table_name_value

    column_types_value = kwargs.pop("column_types", None)
    if column_types_value is not None and not isinstance(column_types_value, dict):
        raise MorphApiError(
            "Invalid **kwargs provided: 'column_types' must be a dictionary."
        )
    column_types: Optional[Dict[str, str]] = column_types_value

    # DataFrame to be processed
    data: pd.DataFrame
    if isinstance(args[0], RefResponse):
        if args[0].cell_type != "sql":
            raise MorphApiError(f"Cell {args[0].alias} is not a SQL cell")
        if args[0].cell_type != "sql":
            raise MorphApiError(f"Cell {args[0].alias} is not a SQL cell")
        if not args[0].code:
            raise MorphApiError("SQL code is empty")
        sql = args[0].code
        connection_slug = args[0].connection_slug
        data = __execute_sql_impl(sql, connection_slug)
    else:
        data = args[0]
    if not isinstance(data, pd.DataFrame):
        raise MorphApiError("Invalid data type provided. pd.DataFrame is required.")

    sql_utils = SQLUtils(data, table_name, column_types)

    if action == "create":
        sqls = sql_utils.generate_replace_sql()
        __execute_sql_impl(sqls["create_table_sql"])
        if not data.empty:
            __execute_sql_impl(sqls["insert_sql"])
    elif action == "insert":
        __execute_sql_impl(sql_utils.generate_insert_sql())
    elif action == "update":
        if not kwargs.get("key_columns") or not isinstance(kwargs["key_columns"], list):
            raise MorphApiError(
                "Invalid **kwargs provided: key_columns is required for update."
            )
        __execute_sql_impl(sql_utils.generate_update_sql(kwargs["key_columns"]))


def __load_data_impl(
    filepath: str | None = None,
    timestamp: int | None = None,
) -> pd.DataFrame:
    config_from_env = _read_configuration_from_env()
    base_url = config_from_env.base_url
    team_slug = config_from_env.team_slug
    api_key = config_from_env.api_key

    headers = {
        "teamSlug": team_slug,
        "X-Api-Key": api_key,
    }

    split_url = urllib.parse.urlsplit(base_url)
    request_url = urllib.parse.urljoin(
        _canonicalize_base_url(base_url),
        f"{split_url.path}/resource/morph-storage/download-url",
    )

    query_params = {}
    if filepath is not None:
        query_params["filename"] = filepath
    if timestamp is not None:
        query_params["timestamp"] = str(timestamp)
    request_url += f"?{urllib.parse.urlencode(query_params)}"

    try:
        response = requests.get(request_url, headers=headers)
    except Timeout:
        raise MorphApiError("Process Timeout while executing load_data")
    except Exception as e:
        raise MorphApiError(f"{e}")

    response_body = handle_morph_response(response)

    try:
        structured_response_body = SignedUrlResponse(
            url=response_body["preSignedDownloadUrl"]
        )
        df = convert_signed_url_response_to_dataframe(structured_response_body)
        return df
    except Exception as e:
        raise MorphApiError(f"load_data error: {e}")


MORPH_STORAGE_PREFIX = "morph-storage://"


def _get_pre_signed_url_path(file_path: str, team_slug: str, database_id: str) -> str:
    if file_path.startswith(MORPH_STORAGE_PREFIX):
        return file_path
    return "{}vm/{}/{}/{}".format(
        MORPH_STORAGE_PREFIX,
        team_slug,
        database_id,
        file_path if not file_path.startswith("/") else file_path[1:],
    )


# ===============================================
#
# Functions
#
# ===============================================
def execute_sql(*args: Union[RefResponse, str]) -> pd.DataFrame:
    """
    Execute SQL query
    """
    sql: str = args[0] if isinstance(args[0], str) else ""
    connection_slug: str | None = None

    # If the first argument is a RefResponse, extract the SQL code and connection slug
    if args and isinstance(args[0], RefResponse):
        if args[0].cell_type != "sql":
            raise MorphApiError(f"Cell {args[0].alias} is not a SQL cell")
        if not args[0].code:
            raise MorphApiError("SQL code is empty")
        sql = args[0].code
        connection_slug = args[0].connection_slug

    return __execute_sql_impl(sql, connection_slug)


def ref(reference: str) -> RefResponse:
    """
    Get the reference cell information
    @param: reference: The name of the reference cell alias
    """
    project_root = MorphYaml.find_abs_project_root_dir()
    db_manager = SqliteDBManager(project_root)

    resource = MorphYaml.find_resource_by_alias(reference, project_root, db_manager)
    if not resource:
        raise MorphApiError(f"Reference cell {reference} not found")

    return RefResponse(
        cell_type=MorphYaml.get_cell_type(resource.path),
        filepath=resource.path,
        alias=reference,
        code=open(resource.path, "r").read(),
        connection_slug=resource.connection,
    )


def read_dir(target_dir: str = "/") -> List[str]:
    """
    Read directories
    if the directory is in the data directory, it will also list the storage directories
    """
    project_root = MorphYaml.find_abs_project_root_dir()
    expanded_target_dir = os.path.expanduser(target_dir)
    abs_dir_path = OsUtils.normalize_path(expanded_target_dir, project_root)

    dirs = os.listdir(abs_dir_path)
    if abs_dir_path.startswith(os.path.join(project_root, "data")):
        storage_dirs = __list_storage_dirs(abs_dir_path, 1)
        if storage_dirs is not None:
            for storage_dir in storage_dirs.directories:
                dirs.append(storage_dir.name)
            for storage_file in storage_dirs.files:
                dirs.append(storage_file.name)

    return list(set(dirs))


def get_file(*args, **kwargs):
    """
    Get the file path or URL of the file
    """
    if args and isinstance(args[0], RefResponse):
        ref_dict = {
            "filepath": args[0].filepath,
        }
        return __get_file_impl(**ref_dict, **kwargs)
    else:
        return __get_file_impl(*args, **kwargs)


def get_data_path(*args, **kwargs):
    """
    Get the data path or URL of the data
    @param: args: RefResponse or filepath, specific_dirpath, specific_filepath
    """
    if args and isinstance(args[0], RefResponse):
        ref_dict = {
            "filepath": args[0].filepath,
        }
        if len(args) > 1:
            ref_dict["specific_dirpath"] = args[1]
        if len(args) > 2:
            ref_dict["specific_filepath"] = args[2]
        return __get_data_path_impl(**ref_dict, **kwargs)
    else:
        return __get_data_path_impl(*args, **kwargs)


def create_table(
    *args: Union[RefResponse, pd.DataFrame],
    **kwargs: Union[str, int, bool],
) -> None:
    """
    Create a table and insert data
    """
    __process_records("create", *args, **kwargs)


def insert_records(
    *args: Union[RefResponse, pd.DataFrame],
    **kwargs: Union[str, int, bool],
) -> None:
    """
    Insert records into the table
    """
    __process_records("insert", *args, **kwargs)


def update_records(
    *args: Union[RefResponse, pd.DataFrame],
    **kwargs: Union[str, int, bool, List[str]],
) -> None:
    """
    Update records in the table
    """
    __process_records("update", *args, **kwargs)


def generate_report(
    refs: list[RefResponse],
    prompt: Optional[str] = None,
    language: Optional[str] = None,
) -> str:
    """
    Generate report from the references
    """
    config_from_env = _read_configuration_from_env()
    database_id = config_from_env.database_id
    base_url = config_from_env.base_url
    team_slug = config_from_env.team_slug
    api_key = config_from_env.api_key
    canvas = config_from_env.canvas

    if "dashboard-api" not in base_url:
        base_url = base_url.replace("api", "dashboard-api")

    for ref in refs:
        if ref.cell_type != "python":
            raise MorphApiError(f"Cell {ref.cell_name} is not a Python cell")  # type: ignore
        elif "@report" in ref.code:  # type: ignore
            raise MorphApiError(
                f"Cell {ref.cell_name}(report cell) is not allowed to be used in report generation."  # type: ignore
            )

    headers = {
        "teamSlug": team_slug,
        "X-Api-Key": api_key,
    }

    url = urllib.parse.urljoin(
        _canonicalize_base_url(base_url),
        "/agent/chat/report",
    )

    request = {
        "databaseId": database_id,
        "canvas": canvas,
        "files": [ref.alias for ref in refs],
        "prompt": prompt,
        "language": language,
    }
    try:
        response = requests.post(url, headers=headers, json=request, verify=True)
    except Timeout:
        raise MorphApiError("Process Timeout while executing generate_report")
    except Exception as e:
        raise MorphApiError(f"generate_report error: {e}")

    response_body = handle_morph_response(response)
    return response_body["report"]  # type: ignore


def send_email(
    refs: list[RefResponse],
    emails: list[str],
    subject: str,
    body: str,
) -> None:
    """
    Send email with attachments
    """
    config_from_env = _read_configuration_from_env()
    database_id = config_from_env.database_id
    base_url = config_from_env.base_url
    team_slug = config_from_env.team_slug
    api_key = config_from_env.api_key

    attchments: List[Dict[str, str]] = []
    for ref in refs:
        if ref.cell_type != "python":
            raise MorphApiError(f"Cell {ref.cell_name} is not a Python cell")  # type: ignore
        url = get_data_path(ref.filepath)
        if url is None:
            continue
        if not url.startswith("http"):
            storage_path = _get_pre_signed_url_path(url, team_slug, database_id)
            url = __get_presigned_url(storage_path)
        filename = os.path.basename(ref.filepath)
        attchments.append({"path": url, "filename": filename})

    if len(attchments) < 1:
        raise MorphApiError("No attachments found")

    headers = {
        "teamSlug": team_slug,
        "X-Api-Key": api_key,
    }

    url = f"{_canonicalize_base_url(base_url)}/{database_id}/python/email"

    request = {
        "attachments": attchments,
        "emails": emails,
        "subject": subject,
        "body": body,
    }

    try:
        response = requests.post(url, headers=headers, json=request, verify=True)
    except Timeout:
        raise MorphApiError("Process Timeout while executing send_email")
    except Exception as e:
        raise MorphApiError(f"send_email error: {e}")

    handle_morph_response(response)


def load_data(
    *args: LoadDataParams, **kwargs: Dict[str, Union[str, int, bool]]
) -> Optional[DataFrame]:
    project_root = MorphYaml.find_abs_project_root_dir()
    db_manager = SqliteDBManager(project_root)

    if args and isinstance(args[0], RefResponse):
        if args[0].cell_type == "sql":
            ref_dict = {
                "sql": args[0].code,
                "connection_slug": args[0].connection_slug,
            }
            return __execute_sql_impl(**ref_dict, **kwargs)  # type: ignore
        elif args[0].cell_type == "file":
            if not args[0].filepath.startswith(MORPH_STORAGE_PREFIX):
                return convert_filepath_to_df(args[0].filepath)
            ref_dict = {
                "filepath": args[0].filepath,
            }
            return __load_data_impl(**ref_dict, **kwargs)  # type: ignore
        elif args[0].cell_type == "python":
            filepath = __get_data_path_impl(args[0].filepath)
            if filepath is None:
                return filepath
            if not filepath.startswith(MORPH_STORAGE_PREFIX):
                return convert_filepath_to_df(filepath)
            return __load_data_impl(filepath, **kwargs)  # type: ignore
        else:
            raise MorphApiError(f"Cell {args[0].cell_name} is not a valid cell type")  # type: ignore
    elif "type" in args[0]:  # type: ignore
        config_from_env = _read_configuration_from_env()
        team_slug = config_from_env.team_slug
        database_id = config_from_env.database_id

        if args[0]["type"] == "sql":  # type: ignore
            omitted_args = {k: v for k, v in args[0].items() if k != "type"}  # type: ignore
            return __execute_sql_impl(**omitted_args, **kwargs)  # type: ignore
        elif args[0]["type"] == "file":  # type: ignore
            omitted_args = {k: v for k, v in args[0].items() if k != "type"}  # type: ignore
            if not omitted_args["filepath"].startswith(MORPH_STORAGE_PREFIX):  # type: ignore
                filepath = os.path.join(
                    project_root,
                    os.path.realpath(omitted_args["filepath"]),  # type: ignore
                )
                if os.path.exists(filepath):
                    return convert_filepath_to_df(filepath)
                else:
                    storage_path = _get_pre_signed_url_path(
                        filepath, team_slug, database_id
                    )
                    return __load_data_impl(storage_path, **kwargs)  # type: ignore
            return __load_data_impl(**omitted_args, **kwargs)  # type: ignore
        elif args[0]["type"] == "python":  # type: ignore
            omitted_args = {k: v for k, v in args[0].items() if k != "type"}  # type: ignore
            reference = omitted_args["reference"]
            if not reference:
                return None
            resource = MorphYaml.find_resource_by_alias(
                str(reference), project_root, db_manager
            )
            filepath = resource.path if resource else None
            if not filepath:
                return None
            if not filepath.startswith(MORPH_STORAGE_PREFIX):
                filepath = os.path.join(project_root, os.path.realpath(filepath))
                if os.path.exists(filepath):
                    return convert_filepath_to_df(filepath)
                else:
                    storage_path = _get_pre_signed_url_path(
                        filepath, team_slug, database_id
                    )
                    return __load_data_impl(storage_path, **kwargs)  # type: ignore
            return __load_data_impl(filepath, **kwargs)  # type: ignore
        else:
            raise ValueError("Invalid data cell type provided.")
    else:
        raise ValueError("Invalid data cell type provided.")
