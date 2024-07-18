import base64
import logging
import os
import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from typing import Any, DefaultDict, Dict, List, Optional, Set, Union

import click
import yaml

from morph.task.constant.project_config import ProjectConfig
from morph.task.utils.decorator import DecoratorParser
from morph.task.utils.os import OsUtils
from morph.task.utils.sqlite import SqliteDBManager

YAML_IGNORE_DIRS = ["/private/tmp", "/tmp"]


@dataclass
class Resource:
    alias: str
    path: str
    connection: Optional[str] = None
    output_paths: Optional[List[str]] = None
    public: Optional[bool] = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alias": self.alias,
            "path": self.path,
            "connection": self.connection,
            "output_paths": self.output_paths,
            "public": self.public,
        }

    def _replace_output_placeholders(
        self, output_file: str, logger: logging.Logger = logging.getLogger()
    ) -> List[str]:
        # Definition of placeholder functions that can be used in the output_path
        placeholder_map: Dict[str, str] = {
            "{now()}": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "{unix()}": str(int(time.time() * 1000)),
        }

        # Replace placeholders in the output path
        for placeholder, expanded in placeholder_map.items():
            if placeholder in output_file:
                output_file = output_file.replace(placeholder, expanded)

        # Replace ext() placeholder; ext() can produce multiple output_paths
        output_files: List[str] = []
        if "{ext()}" in output_file:
            extensions = MorphYaml.analyze_output_extensions(self.path)
            output_files = [output_file.replace("{ext()}", ext) for ext in extensions]
        else:
            output_files = [output_file]

        # Validate the output paths
        validated_outputs = []
        for f in output_files:
            # Check for undefined placeholders
            if "{" in f and "}" in f:
                logger.warning(
                    f"Unrecognized placeholder found in the output_paths: {f}. Cell output not saved."
                )
                continue

            # Avoid output_file to have multiple extensions
            dirname = os.path.dirname(f)
            basename = os.path.splitext(os.path.basename(f))[0].replace(".", "")
            ext = os.path.splitext(os.path.basename(f))[1]
            validated_outputs.append(os.path.join(dirname, f"{basename}{ext}"))
        return validated_outputs

    @staticmethod
    def _write_output_file(
        output_file: str,
        output: Union[str, bytes],
    ) -> None:
        if not os.path.exists(os.path.dirname(output_file)):
            os.makedirs(os.path.dirname(output_file))

        mode = "wb" if isinstance(output, bytes) else "w"
        with open(output_file, mode) as f:
            f.write(output or "")

    def save_output_to_file(
        self,
        output: Union[str, bytes, List[Union[str, bytes]]],
        logger: logging.Logger = logging.getLogger(),
    ) -> "Resource":
        processed_output_paths = []

        for original_output_path in self.output_paths or []:
            output_files = self._replace_output_placeholders(
                original_output_path, logger
            )
            for output_file in output_files:
                if isinstance(output, list):
                    # For multiple outputs, HTML and PNG outputs are saved as files
                    for raw_output in output:
                        should_save_as_html = output_file.endswith(".html")
                        should_save_as_png = output_file.endswith(".png")

                        is_html_encoded = (
                            isinstance(raw_output, str)
                            and re.compile(r"<[^>]+>").search(raw_output) is not None
                        )
                        if should_save_as_html and not is_html_encoded:
                            continue

                        is_base64_encoded = (
                            isinstance(raw_output, str)
                            and re.match(r"^[A-Za-z0-9+/=]*$", raw_output) is not None
                        )
                        if should_save_as_png and not is_base64_encoded:
                            continue

                        if should_save_as_png:
                            base64.b64decode(raw_output, validate=True)
                            raw_output = base64.b64decode(raw_output)

                        self._write_output_file(output_file, raw_output)
                        processed_output_paths.append(output_file)
                        logger.info(f"Cell output saved to: {output_file}")
                else:
                    self._write_output_file(output_file, output)
                    processed_output_paths.append(output_file)
                    logger.info(f"Cell output saved to: {output_file}")

        self.output_paths = processed_output_paths
        return self


@dataclass
class MorphYaml:
    version: str
    resources: Dict[str, Dict[str, Any]]
    canvases: Dict[str, Dict[str, Any]]

    @staticmethod
    def load_yaml(project_root_path: str) -> "MorphYaml":
        morph_yaml_path = os.path.join(project_root_path, ProjectConfig.MORPH_YAML)
        if not os.path.isfile(morph_yaml_path):
            raise FileNotFoundError(f"morph.yaml not found in {project_root_path}")

        with open(morph_yaml_path, "r") as file:
            data = yaml.safe_load(file)

        return MorphYaml.from_dict(data)

    def save_yaml(self, project_root_path: str) -> None:
        morph_yaml_path = os.path.join(project_root_path, ProjectConfig.MORPH_YAML)

        yaml_content = yaml.dump(self.to_dict(), sort_keys=False)

        headers = {
            "ja": """\
# -------------------------------------------------------------------------------------
# このYAMLファイルはMorphプロジェクトの設定を定義します。
# リソース（例：PythonおよびSQLセル）やキャンバスの定義が含まれます。
# resources セクションでは、スクリプトのパスおよびその出力場所を指定します。
# canvases セクションでは、これらのリソースを視覚的にレイアウトします。
# -------------------------------------------------------------------------------------
#
# [output_paths]
# output_pathsフィールドの前提条件：
#   - output_pathsは文字列のリストでなければならず、少なくとも1つのパスを含む必要があります。
# output_pathsで使用できるプレースホルダー関数：
#   - {ext()}  : 結果の内容に基づいて出力拡張子を決定します
#   - {now()}  : YYYYMMDD_HHMMSS形式で現在の日付と時刻を出力します
#   - {unix()} : ミリ秒単位で13桁のUNIXタイムスタンプを出力します
# 例：
#   - output_paths: ["data/outputs/example_python_cell/result_{unix()}{ext()}"]""",
            "en": """\
# -------------------------------------------------------------------------------------
# This YAML file defines the configuration for a Morph project.
# It includes definitions for resources (e.g., Python and SQL cells) and canvases.
# The resources section specifies the paths to the scripts and their output locations.
# The canvases section organizes these resources into a visual layout.
# -------------------------------------------------------------------------------------
#
# [output_paths]
# Prerequisites for the output_paths field:
#   - The output_paths must be a list of strings, which contains at least one path.
# Placeholder functions that can be used in the output_paths:
#   - {ext()}  : Determines the output extension based on the result content
#   - {now()}  : Outputs the current date and time in the format YYYYMMDD_HHMMSS
#   - {unix()} : Outputs a 13-digit UNIX timestamp in milliseconds
# Example:
#   - output_paths: ["data/outputs/example_python_cell/result_{unix()}{ext()}"]""",
        }

        # Insert comments
        yaml_content = f"{headers['en']}\n\n{yaml_content}"

        with open(morph_yaml_path, "w") as file:
            file.write(yaml_content)

    def to_dict(self) -> dict:
        updated_canvases = {}
        for canvas, cells_dict in self.canvases.items():
            if "cells" not in cells_dict:
                updated_canvases[canvas] = {"cells": cells_dict}
            else:
                updated_canvases[canvas] = cells_dict
        return {
            "version": self.version,
            "resources": self.resources,
            "canvases": updated_canvases,
        }

    @staticmethod
    def from_dict(data: dict) -> "MorphYaml":
        resources = data.get("resources", {})
        canvases = {
            canvas: cells.get("cells", cells)
            for canvas, cells in data.get("canvases", {}).items()
        }
        return MorphYaml(
            version=data["version"], resources=resources, canvases=canvases
        )

    @staticmethod
    def find_abs_project_root_dir(abs_filepath: Optional[str] = None) -> str:
        current_dir = (
            abs_filepath
            if abs_filepath and os.path.isabs(abs_filepath)
            else os.getcwd()
        )

        # /tmp などの再起動によって失われるファイルでの実行は実行場所を起点とする
        for ignore_dir in YAML_IGNORE_DIRS:
            if ignore_dir in current_dir:
                current_dir = os.getcwd()

        while current_dir != os.path.dirname(current_dir):
            morph_yaml_path = os.path.join(current_dir, ProjectConfig.MORPH_YAML)
            if os.path.isfile(morph_yaml_path):
                return os.path.abspath(os.path.dirname(morph_yaml_path))
            current_dir = os.path.dirname(current_dir)
        raise FileNotFoundError(
            f"{ProjectConfig.MORPH_YAML} not found in the current directory or any parent directories."
        )

    @staticmethod
    def find_resource_by_alias(
        alias: str, project_root: str, db_manager: SqliteDBManager
    ) -> Optional[Resource]:
        # First, search in the SQLite database
        resource = db_manager.get_resource_by_alias(alias)
        if resource:
            if not resource.get("alias") or not resource.get("path"):
                return None

            Resource(
                alias=resource["alias"],
                path=OsUtils.normalize_path(resource["path"], project_root),
                connection=resource.get("connection"),
                output_paths=[
                    OsUtils.normalize_path(p, project_root)
                    for p in resource.get("output_paths", [])
                ],
                public=resource.get("public"),
            )

        # If not found, load and search in the YAML file
        morph_yaml = MorphYaml.load_yaml(project_root)
        resource = morph_yaml.resources.get(alias)
        if resource and resource.get("path"):
            # Sync to SQLite
            replaced = db_manager.replace_resource_record(
                alias, resource["path"], resource
            )
            return Resource(
                alias=replaced["alias"],
                path=OsUtils.normalize_path(replaced["path"], project_root),
                connection=replaced.get("connection"),
                output_paths=[
                    OsUtils.normalize_path(p, project_root)
                    for p in replaced.get("output_paths", [])
                ],
                public=replaced.get("public"),
            )

        return None

    @staticmethod
    def find_resource_by_path(
        path: str, project_root: str, db_manager: SqliteDBManager
    ) -> Optional[Resource]:
        normalized_path = OsUtils.normalize_path(path, project_root)

        # /tmp などの再起動によって失われるファイルでの実行はYAMLファイルに記録しない
        for ignore_dir in YAML_IGNORE_DIRS:
            if ignore_dir in normalized_path:
                return None

        # First, search in the SQLite database
        resource = db_manager.get_resource_by_path(normalized_path)
        if resource:
            if not resource.get("alias") or not resource.get("path"):
                return None

            return Resource(
                alias=resource["alias"],
                path=OsUtils.normalize_path(resource["path"], project_root),
                connection=resource.get("connection"),
                output_paths=[
                    OsUtils.normalize_path(p, project_root)
                    for p in resource.get("output_paths", [])
                ],
                public=resource.get("public"),
            )

        # If not found, load and search in the YAML file
        morph_yaml = MorphYaml.load_yaml(project_root)
        for alias, resource in morph_yaml.resources.items():
            resource_path = OsUtils.normalize_path(resource["path"], project_root)
            if resource_path == normalized_path:
                # Sync to SQLite
                replaced = db_manager.replace_resource_record(
                    alias, normalized_path, resource
                )
                return Resource(
                    alias=replaced["alias"],
                    path=OsUtils.normalize_path(replaced["path"], project_root),
                    connection=replaced.get("connection"),
                    output_paths=[
                        OsUtils.normalize_path(p, project_root)
                        for p in replaced.get("output_paths", [])
                    ],
                    public=replaced.get("public"),
                )

        return None

    @staticmethod
    def analyze_output_extensions(abs_filename: str) -> List[str]:
        ext = os.path.splitext(os.path.basename(abs_filename))[1]
        if ext == ".sql":
            return [".csv"]
        else:
            # Analyze decorators to determine the output extension
            code = open(abs_filename, "r").read()
            decorators = DecoratorParser.get_decorators(code)
            decorator_name = None
            for decorator in decorators:
                if isinstance(decorator, dict):
                    decorator_name = decorator.get("name")
                else:
                    decorator_name = decorator
            if decorator_name == "visualize":
                return [".html", ".png"]
            elif decorator_name == "transform":
                return [".csv"]
            elif decorator_name == "report":
                return [".md"]
            elif decorator_name == "api":
                return [".json"]
            else:
                return [".txt"]

    @staticmethod
    def _generate_default_output_path(
        alias: str,
        abs_filename: str,
        project_root: str,
        output_dir: Optional[str] = None,
    ) -> List[str]:
        output_dir = output_dir or OsUtils.normalize_path(
            os.path.join(ProjectConfig.OUTPUTS_DIR, alias), project_root
        )
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        return [os.path.join(output_dir, "result{ext()}")]

    @staticmethod
    def find_or_create_resource_by_path(
        path: str, project_root: str, db_manager: SqliteDBManager
    ) -> Resource:
        resource = MorphYaml.find_resource_by_path(path, project_root, db_manager)
        if resource:
            return resource

        # Generate output path
        abs_path = OsUtils.normalize_path(path, project_root)

        # Generate new alias if the resource is not defined yet in the morph.yaml
        base_name = os.path.splitext(os.path.basename(abs_path))[0]
        new_alias = base_name

        # /tmp などの再起動によって失われるファイルでの実行はYAMLファイルに記録しない
        for ignore_dir in YAML_IGNORE_DIRS:
            if ignore_dir in abs_path:
                output_dir = OsUtils.normalize_path(
                    os.path.join(ProjectConfig.OUTPUTS_DIR, new_alias), ignore_dir
                )
                output_paths = MorphYaml._generate_default_output_path(
                    new_alias, abs_path, project_root, output_dir
                )
                return Resource(
                    alias=abs_path,  # To avoid duplicate alias, fill with abs_path
                    path=abs_path,
                    connection=None,
                    output_paths=output_paths,
                    public=None,
                )

        # Loading morph.yaml to avoid duplicate alias
        alias_count: DefaultDict[str, int] = defaultdict(int)
        morph_yaml = MorphYaml.load_yaml(project_root)
        for alias in morph_yaml.resources.keys():
            if alias.startswith(base_name):
                alias_count[alias] += 1

        if new_alias in morph_yaml.resources:
            new_alias = f"{base_name}_{alias_count[base_name]}"

        while new_alias in morph_yaml.resources:
            alias_count[base_name] += 1
            new_alias = f"{base_name}_{alias_count[base_name]}"

        morph_yaml.resources[new_alias] = {
            "path": abs_path,
            "output_paths": MorphYaml._generate_default_output_path(
                new_alias, abs_path, project_root
            ),
        }

        # Sync new resource to SQLite
        db_manager.replace_resource_record(
            new_alias, abs_path, morph_yaml.resources[new_alias]
        )

        # Save morph.yaml
        morph_yaml.save_yaml(project_root)

        click.echo(
            click.style(f"Resource {path} added with alias {new_alias}", fg="green")
        )

        return Resource(
            alias=new_alias,
            path=abs_path,
            connection=morph_yaml.resources[new_alias].get("connection"),
            output_paths=morph_yaml.resources[new_alias]["output_paths"],
            public=morph_yaml.resources[new_alias].get("public"),
        )

    @staticmethod
    def find_or_create_resource_by_alias(
        alias: str, project_root: str, db_manager: SqliteDBManager
    ) -> Resource:
        resource = MorphYaml.find_resource_by_alias(alias, project_root, db_manager)
        if not resource:
            raise FileNotFoundError(f"Alias {alias} not found.")
        if not resource.path:
            raise FileNotFoundError(f"Resource path not found for alias {alias}.")

        if len(resource.output_paths or []) > 0:
            return Resource(
                alias=resource.alias,
                path=OsUtils.normalize_path(resource.path, project_root),
                connection=resource.connection,
                output_paths=resource.output_paths or [],
                public=resource.public,
            )

        # Generate output path
        abs_path = OsUtils.normalize_path(resource.path, project_root)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Resource file {resource.path} not found.")
        output_paths = MorphYaml._generate_default_output_path(
            alias, abs_path, project_root
        )

        # Load morph.yaml and update output_paths
        morph_yaml = MorphYaml.load_yaml(project_root)
        morph_yaml.resources[alias]["output_paths"] = output_paths

        # Sync new resource to SQLite
        db_manager.replace_resource_record(alias, abs_path, morph_yaml.resources[alias])

        # Save morph.yaml
        morph_yaml.save_yaml(project_root)

        return Resource(
            alias=alias,
            path=abs_path,
            connection=resource.connection,
            output_paths=output_paths,
            public=resource.public,
        )

    @staticmethod
    def preprocess_output_paths(
        alias: str, project_root: str, db_manager: SqliteDBManager
    ) -> None:
        """
        outputに異なる拡張子の値が出力される場合にoutput_pathを確認する
        visuzlizeの場合以外にパターンがある場合はロジックを追加する
        """
        # リソースを取得
        resource = MorphYaml.find_resource_by_alias(alias, project_root, db_manager)
        if not resource:
            raise FileNotFoundError(f"Alias {alias} not found.")
        if not resource.path:
            raise FileNotFoundError(f"Resource path not found for alias {alias}.")

        output_paths = resource.output_paths or []

        if len(output_paths) == 0 or (
            len(output_paths) == 1
            and (output_paths[0].endswith(".html") or output_paths[0].endswith(".png"))
        ):
            # デフォルトのoutput_pathを生成
            output_dir = os.path.join(
                project_root, "src", ProjectConfig.OUTPUTS_DIR, alias
            )
            base_output_path = os.path.join(output_dir, "result")
            default_output_paths = [
                f"{base_output_path}.html",
                f"{base_output_path}.png",
            ]

            if len(output_paths) == 1:
                base_output_path = os.path.splitext(output_paths[0])[0]
                if output_paths[0].endswith(".html"):
                    output_paths = [output_paths[0], base_output_path + ".png"]
                elif output_paths[0].endswith(".png"):
                    output_paths = [base_output_path + ".html", output_paths[0]]
                else:
                    output_paths = default_output_paths
            else:
                output_paths = default_output_paths

        elif len(output_paths) == 2:
            # output_pathが2つ指定されている場合の処理
            ext_0 = os.path.splitext(output_paths[0])[1]
            ext_1 = os.path.splitext(output_paths[1])[1]

            if {ext_0, ext_1} == {".html", ".png"}:
                # 順番が逆の場合は入れ替える
                if ext_0 == ".png" and ext_1 == ".html":
                    output_paths = [output_paths[1], output_paths[0]]
            else:
                # 拡張子が完全に異なる場合はエラーを吐く
                raise ValueError(
                    "Output paths must include both .html and .png extensions."
                )

        # morph.yamlをロードしてoutput_pathを更新
        morph_yaml = MorphYaml.load_yaml(project_root)
        morph_yaml.resources[alias]["output_paths"] = output_paths

        # SQLiteに新しいリソースを同期
        abs_path = OsUtils.normalize_path(resource.path, project_root)
        db_manager.replace_resource_record(alias, abs_path, morph_yaml.resources[alias])

        # morph.yamlを保存
        morph_yaml.save_yaml(project_root)

    def get_dag_execution_order(self, canvas_name: str, start_alias: str) -> List[str]:
        dag = {}
        visited = set()
        queue = deque([start_alias])

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            cell = self.canvases[canvas_name].get(current)
            if cell:
                parents = cell.get("parents", [])
                dag[current] = parents
                for parent in parents:
                    if parent not in visited:
                        queue.append(parent)

        execution_order: List[str] = []
        executed: Set[str] = set()
        for node in dag:
            self._collect_execution_order(node, executed, dag, execution_order)

        return execution_order

    def _collect_execution_order(self, node, executed, dag, execution_order):
        if node in executed:
            return

        for parent in dag.get(node, []):
            self._collect_execution_order(parent, executed, dag, execution_order)

        execution_order.append(node)
        executed.add(node)

    @staticmethod
    def get_cell_type(path: str) -> str:
        if os.path.isdir(path):
            return "directory"
        elif os.path.isfile(path):
            extension_mapping = {
                "sql": "sql",
                "py": "python",
            }
            ext = os.path.splitext(path)[1][1:]
            return extension_mapping.get(ext, "file")
        else:
            raise FileNotFoundError(f"File not found: {path}")
