import configparser
import json
import os
import time
from typing import Any, Dict, List, Optional, TypedDict, Union

import click
import requests
from dotenv import load_dotenv
from line_profiler import line_profiler
from morphdb_utils.type import SignedUrlResponse
from pandas import DataFrame

from morph.cli.flags import Flags
from morph.task.base import BaseTask
from morph.task.constant.project_config import ProjectConfig
from morph.task.utils.code_execution import execute_user_code
from morph.task.utils.decorator import DecoratorParser
from morph.task.utils.logging import get_morph_logger
from morph.task.utils.morph import MorphYaml
from morph.task.utils.sqlite import RunStatus, SqliteDBManager
from morph.task.utils.timer import TimeoutException, run_with_timeout
from morph.task.utils.timezone import TimezoneManager


class RunTask(BaseTask):
    def __init__(self, args: Flags):
        super().__init__(args)

        # validate credentials
        config_path = ProjectConfig.MORPH_CRED_PATH
        if not os.path.exists(config_path):
            click.echo(
                click.style(
                    f"Error: No credentials found in {config_path}.",
                    fg="red",
                )
            )
            raise FileNotFoundError(f"No credentials found in {config_path}.")

        # read credentials
        config = configparser.ConfigParser()
        config.read(config_path)
        if not config.sections():
            click.echo(
                click.style(
                    f"Error: No credentials entries found in {config_path}.",
                    fg="red",
                )
            )
            raise FileNotFoundError(f"No credentials entries found in {config_path}.")

        # NOTE: vm内ではセクションが必ず1つなので、'default' セクションを指定している
        self.team_slug: str = config.get("default", "team_slug")
        self.app_url: str = config.get("default", "app_url")
        self.database_id: str = config.get("default", "database_id")
        self.api_key: str = config.get("default", "api_key")

        # create setup code
        self.setup_code: str = f"""\
from io import StringIO
import pandas as pd

import os
os.environ["MORPH_DATABASE_ID"] = "{self.database_id}"
os.environ["MORPH_BASE_URL"] = "{self.app_url}"
os.environ["MORPH_TEAM_SLUG"] = "{self.team_slug}"
os.environ["MORPH_API_KEY"] = "{self.api_key}"
"""

        # parse arguments
        self.filename: str = os.path.normpath(args.FILENAME)
        self.run_id: str = self.args.RUN_ID or f"{int(time.time() * 1000)}"
        self.is_dag: bool = args.DAG or False
        self.is_dry_run: bool = args.DRY_RUN or False
        self.canvas = args.CANVAS

        try:
            start_dir = self.filename if os.path.isabs(self.filename) else "./"
            self.project_root = MorphYaml.find_abs_project_root_dir(start_dir)
        except FileNotFoundError as e:
            click.echo(click.style(str(e), fg="red"))
            raise e

        # Initialize database
        self.db_manager = SqliteDBManager(self.project_root)
        self.db_manager.initialize_database()

        if os.path.splitext(os.path.basename(self.filename))[1]:
            # If filepath is provided, find or create resource by path
            if not os.path.isfile(self.filename):
                click.echo(
                    click.style(
                        f"Error: File {self.filename} not found.",
                        fg="red",
                    )
                )
                raise FileNotFoundError(f"Error: File {self.filename} not found.")
            self.resource = MorphYaml.find_or_create_resource_by_path(
                self.filename, self.project_root, self.db_manager
            )
        else:
            # Find the file in morph.yaml if alias is provided
            resource = MorphYaml.find_resource_by_alias(
                self.filename, self.project_root, self.db_manager
            )
            if not resource:
                click.echo(
                    click.style(
                        f"Error: A resource with alias {self.filename} not found.",
                        fg="red",
                    )
                )
                raise FileNotFoundError(
                    f"A resource with alias {self.filename} not found."
                )
            self.resource = resource

        self.filename = self.resource.path
        self.basename = os.path.splitext(os.path.basename(self.filename))[0]
        self.ext = os.path.splitext(os.path.basename(self.filename))[1]
        self.cell_alias = self.resource.alias

        # Set up run directory
        self.runs_dir = os.path.normpath(
            os.path.join(
                ProjectConfig.RUNS_DIR,
                self.canvas if self.canvas else "",
                self.run_id,
            )
        )
        if not os.path.exists(self.runs_dir):
            os.makedirs(self.runs_dir)

        # Set up logger
        log_filename = f"{os.path.splitext(os.path.basename(self.cell_alias))[0]}.log"
        self.log_path = os.path.join(self.runs_dir, log_filename)
        self.logger = get_morph_logger(self.log_path)

        # load .env in project root and set timezone
        dotenv_path = os.path.join(self.project_root, ".env")
        load_dotenv(dotenv_path)
        self.setup_code += self._load_env_from_cloud()
        if self.canvas:
            self.setup_code += f'os.environ["MORPH_CANVAS"] = "{self.canvas}"\n'
        desired_tz = os.getenv("TZ")
        if desired_tz is not None:
            tz_manager = TimezoneManager()
            if not tz_manager.is_valid_timezone(desired_tz):
                self.logger.error(f"Invalid TZ value in .env: {desired_tz}")
                raise ValueError(f"Invalid TZ value in .env: {desired_tz}")
            if desired_tz != tz_manager.get_current_timezone():
                tz_manager.change_timezone(desired_tz)

    def _finalize_run(
        self,
        cell_alias: str,
        final_state: str,
        output: Any,
        error: Optional[Dict[str, str]] = None,
    ) -> None:
        self.resource = self.resource.save_output_to_file(output, self.logger)
        self.db_manager.update_run_record(
            self.run_id,
            self.canvas,
            cell_alias,
            final_state,
            error,
            self.resource.output_paths,
        )

    def run(self) -> None:
        if self.is_dry_run:
            if self.is_dag:
                morph_yaml = MorphYaml.load_yaml(self.project_root)
                execution_order = morph_yaml.get_dag_execution_order(
                    self.canvas, self.cell_alias
                )
            else:
                execution_order = [self.cell_alias]

            # Format execution order as a single line list
            execution_order_str = ", ".join(execution_order)
            self.logger.info(
                f"Dry run mode enabled. Following cells will be executed: [{execution_order_str}]"
            )
            return

        # NOTE: morphdb-utilsから相対参照できるようにカレントディレクトリを変更
        os.chdir(os.path.dirname(self.filename))
        if self.is_dag:
            self._run_dag()
        else:
            self._execute_cell(self.cell_alias)

    def _run_dag(self) -> None:
        morph_yaml = MorphYaml.load_yaml(self.project_root)
        execution_order = morph_yaml.get_dag_execution_order(
            self.canvas, self.cell_alias
        )
        for cell in execution_order:
            self._execute_cell(cell, is_dag=True)

    def _execute_cell(self, cell: str, is_dag: bool = False) -> None:
        if is_dag:
            # Override self variables if running in DAG mode
            self.cell_alias = cell
            self.log_path = os.path.join(self.runs_dir, f"{self.cell_alias}.log")
            self.logger = get_morph_logger(self.log_path)
            resource = MorphYaml.find_resource_by_alias(
                self.cell_alias, self.project_root, self.db_manager
            )
            if not resource:
                click.echo(
                    click.style(
                        f"Error: A resource with alias {self.cell_alias} not found.",
                        fg="red",
                    )
                )
                raise FileNotFoundError(
                    f"A resource with alias {self.cell_alias} not found."
                )
            self.resource = resource
            self.filename = self.resource.path

        self.db_manager.insert_run_record(
            self.run_id,
            self.canvas,
            self.cell_alias,
            self.is_dag,
            self.log_path,
        )

        # Execute cell
        if self.ext == ".sql":
            self._run_sql(self.cell_alias)
        elif self.ext == ".py":
            self._run_python(self.cell_alias)
        else:
            text = "Invalid file type. Please specify a .sql or .py file."
            self.logger.error(text)
            self._finalize_run(self.cell_alias, RunStatus.FAILED, None, {"error": text})

    def _run_sql(self, cell: str) -> None:
        self.logger.info(f"Running sql file: {self.filename}")

        try:
            url = f"{self.app_url}/{self.database_id}/sql/csv"
            headers = {
                "x-api-key": self.api_key,
            }
            code = open(self.filename, "r").read()
            request = {"sql": code}
            connection = self.resource.connection
            if connection is not None:
                request["connectionSlug"] = connection

            response = requests.post(
                url=url, headers=headers, json=request, verify=True
            )
            if response.status_code > 500:
                text = f"An error occurred while running the SQL: {response.text}"
                self.logger.error(text)
                self._finalize_run(cell, RunStatus.FAILED, None, {"error": text})
                return
            else:
                response_json = response.json()
                if (
                    "error" in response_json
                    and "subCode" in response_json
                    and "message" in response_json
                ):
                    error_message = response_json["message"]
                    text = f"An error occurred while running the SQL: {error_message}"
                    self.logger.error(text)
                    self._finalize_run(cell, RunStatus.FAILED, None, {"error": text})
                    return
                else:
                    structured_response = SignedUrlResponse(url=response_json["url"])
                    r = requests.get(structured_response.url)
                    self._finalize_run(cell, RunStatus.DONE, r.content)
        except Exception as e:
            text = f"An error occurred while running the SQL: {str(e)}"
            self.logger.error(text)
            self._finalize_run(cell, RunStatus.FAILED, None, {"error": text})
            return

        self.logger.info(f"Successfully ran sql file: {self.filename}")

    def _run_python(self, cell: str) -> None:
        self.logger.info(f"Running python file: {self.filename}")

        try:
            timeout_seconds = -1
            code = open(self.filename, "r").read()
            debug = False
            decorator_name = None
            decorators = DecoratorParser.get_decorators(code)
            for decorator in decorators:
                if isinstance(decorator, dict):
                    decorator_name = decorator.get("name")
                else:
                    decorator_name = decorator

            try:
                result: Union[DataFrame, list, str, dict, None]
                error: Optional[Dict[str, str]]
                profiler: Optional[line_profiler.LineProfiler]
                result, error, profiler, code = run_with_timeout(
                    execute_user_code,
                    timeout_seconds,
                    args=(code, self.setup_code, debug, self.logger),
                )
            except TimeoutException:
                text = (
                    f"Timeout error occurred while running the script: {self.filename}"
                )
                self.logger.error(text)
                self._finalize_run(cell, RunStatus.FAILED, None, {"error": text})
                return
            except Exception as e:
                text = (
                    f"Unexpected error occurred while executing python code: {str(e)}"
                )
                self.logger.error(text)
                self._finalize_run(cell, RunStatus.FAILED, None, {"error": text})
                return

            if error is not None:
                text = f"An python error occurred while running the script: {error}"
                self.logger.error(text)
                self._finalize_run(cell, RunStatus.FAILED, None, {"error": text})
                return

            output: Any
            if decorator_name == "visualize":
                if isinstance(result, list):
                    # [0] = html, [1] = png
                    output = result
                    MorphYaml.preprocess_output_paths(
                        self.cell_alias, self.project_root, self.db_manager
                    )
                else:
                    output = str(result)
            elif decorator_name == "transform":
                if isinstance(result, DataFrame):
                    output = result.to_csv()
                else:
                    output = str(result)
            elif decorator_name == "report":
                if isinstance(result, DataFrame):
                    output = result.to_string()
                else:
                    output = str(result)
            elif decorator_name == "api":
                if isinstance(result, dict):
                    output = json.dumps(result, indent=4)
                else:
                    output = str(result)
            else:
                if isinstance(result, DataFrame):
                    output = result.to_string()
                else:
                    output = str(result)

            self._finalize_run(
                cell,
                RunStatus.DONE,
                output,
                None,
            )
        except Exception as e:
            text = f"An error occurred while running the script: {str(e)}"
            self.logger.error(text)
            self._finalize_run(cell, RunStatus.FAILED, None, {"error": text})
            return

        self.logger.info(f"Successfully ran python file: {self.filename}")

    def _load_env_from_cloud(self) -> str:
        class EnvVarItem(TypedDict):
            key: str
            value: str

        class ResponseJson(TypedDict):
            error: Union[str, None]
            subCode: Union[int, None]
            message: Union[str, None]
            items: List[EnvVarItem]

        url = f"{self.app_url}/{self.database_id}/env-vars"
        headers = {
            "x-api-key": self.api_key,
        }
        try:
            response = requests.get(url=url, headers=headers, verify=True)
            if response.status_code > 500:
                self.logger.error(
                    f"An error occurred while loading environment variables: {response.text}"
                )
                return ""
            else:
                response_json: ResponseJson = response.json()
                if (
                    "error" in response_json
                    and "subCode" in response_json
                    and "message" in response_json
                ):
                    self.logger.error(
                        f"An error occurred while loading environment variables: {response_json['message']}"
                    )
                    return ""
                else:
                    env_vars: str = ""
                    for item in response_json["items"]:
                        key = item["key"]
                        value = item["value"]
                        env_vars += f'os.environ["{key}"] = "{value}"\n'
                    return env_vars
        except Exception as e:
            self.logger.error(
                f"An error occurred while loading environment variables: {str(e)}"
            )
            return ""
