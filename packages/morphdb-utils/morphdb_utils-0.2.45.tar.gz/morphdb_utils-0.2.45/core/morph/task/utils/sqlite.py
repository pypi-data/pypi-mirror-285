import json
import os
import sqlite3
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

import yaml

from morph.task.constant.project_config import ProjectConfig


class RunStatus(str, Enum):
    DONE = "done"
    TIMEOUT = "timeout"
    IN_PROGRESS = "inProgress"
    FAILED = "failed"


class SqliteDBManager:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.db_path = os.path.join(self.project_root, "morph_project.sqlite3")

    def initialize_database(self):
        # Connect to the SQLite database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create "runs" table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT,
                canvas TEXT,
                cell_alias TEXT,
                is_dag BOOLEAN,
                status TEXT,
                error TEXT,
                started_at TEXT,
                ended_at TEXT,
                log TEXT,
                outputs TEXT,
                PRIMARY KEY (run_id, canvas, cell_alias)
            )
            """
        )

        # Create "resources" table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS resources (
                alias TEXT PRIMARY KEY,
                path TEXT,
                attributes TEXT
            )
            """
        )

        # Create indexes for "runs" table
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_runs_cell_alias ON runs(cell_alias)
            """
        )

        # Create indexes for "resources" table
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_resources_path ON resources(path)
            """
        )

        # Commit changes and close the connection
        conn.commit()
        conn.close()

    def insert_run_record(
        self, run_id: str, canvas: str, cell_alias: str, is_dag: bool, log_path: str
    ) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("BEGIN TRANSACTION")
            cursor.execute(
                """
                INSERT INTO runs (run_id, canvas, cell_alias, is_dag, status, started_at, ended_at, log, outputs)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    canvas,
                    cell_alias,
                    is_dag,
                    RunStatus.IN_PROGRESS,
                    datetime.now().isoformat(),
                    None,
                    log_path,
                    None,
                ),
            )
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def update_run_record(
        self,
        run_id: str,
        canvas: Optional[str],
        cell_alias: str,
        new_status: str,
        error: Optional[Union[str, dict, List[str]]] = None,
        outputs: Optional[Union[str, dict, List[str]]] = None,
    ) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        ended_at = datetime.now().isoformat()

        # Ensure error and outputs are JSON serializable strings
        if error is not None and not isinstance(error, str):
            error = json.dumps(error)
        if outputs is not None and not isinstance(outputs, str):
            outputs = json.dumps(outputs)

        try:
            cursor.execute("BEGIN TRANSACTION")
            if canvas is None:
                cursor.execute(
                    """
                    UPDATE runs
                    SET status = ?, error = ?, ended_at = ?, outputs = ?
                    WHERE run_id = ? AND cell_alias = ?
                    """,
                    (new_status, error, ended_at, outputs, run_id, cell_alias),
                )
            else:
                cursor.execute(
                    """
                    UPDATE runs
                    SET status = ?, error = ?, ended_at = ?, outputs = ?
                    WHERE run_id = ? AND canvas = ? AND cell_alias = ?
                    """,
                    (
                        new_status,
                        error,
                        ended_at,
                        outputs,
                        run_id,
                        canvas,
                        cell_alias,
                    ),
                )
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def sync_resources_from_yaml(self) -> None:
        morph_yaml_path = os.path.join(self.project_root, ProjectConfig.MORPH_YAML)
        if not os.path.isfile(morph_yaml_path):
            raise FileNotFoundError(f"morph.yaml not found in {self.project_root}")

        with open(morph_yaml_path, "r") as file:
            morph_config = yaml.safe_load(file)

        resources = morph_config.get("resources", {})

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("BEGIN TRANSACTION")
            cursor.execute("DELETE FROM resources")

            for alias, resource in resources.items():
                attributes = json.dumps(resource)
                cursor.execute(
                    """
                    INSERT INTO resources (alias, path, attributes)
                    VALUES (?, ?, ?)
                    """,
                    (
                        alias,
                        resource.get("path"),
                        attributes,
                    ),
                )
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_resource_by_alias(self, alias: str) -> Optional[dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT alias, path, attributes FROM resources WHERE alias = ?", (alias,)
        )
        resource = cursor.fetchone()

        conn.close()

        if resource:
            attributes = json.loads(resource[2])
            return {
                "alias": resource[0],
                "path": resource[1],
                **attributes,
            }

        return None

    def get_resource_by_path(self, path: str) -> Optional[dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT alias, path, attributes FROM resources WHERE path = ?", (path,)
        )
        resource = cursor.fetchone()

        conn.close()

        if resource:
            attributes = json.loads(resource[2])
            return {
                "alias": resource[0],
                "path": resource[1],
                **attributes,
            }

        return None

    def replace_resource_record(self, alias: str, path: str, attributes: dict) -> dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("BEGIN TRANSACTION")

            # Check if the record exists
            cursor.execute(
                """
                SELECT 1 FROM resources WHERE alias = ?
                """,
                (alias,),
            )
            exists = cursor.fetchone()

            # If the record exists, delete it
            if exists:
                cursor.execute(
                    """
                    DELETE FROM resources WHERE alias = ?
                    """,
                    (alias,),
                )

            # Insert new record
            cursor.execute(
                """
                INSERT INTO resources (alias, path, attributes)
                VALUES (?, ?, ?)
                """,
                (
                    alias,
                    path,
                    json.dumps(attributes),
                ),
            )

            conn.commit()

            return {
                "alias": alias,
                "path": path,
                **attributes,
            }
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
