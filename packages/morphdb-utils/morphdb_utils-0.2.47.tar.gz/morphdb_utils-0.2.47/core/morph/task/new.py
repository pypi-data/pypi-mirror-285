import os

import click

from morph.cli.flags import Flags
from morph.task.base import BaseTask
from morph.task.constant.project_config import ProjectConfig
from morph.task.utils.morph import MorphYaml
from morph.task.utils.os import OsUtils
from morph.task.utils.sqlite import SqliteDBManager

LANG = "en"


class NewTask(BaseTask):
    def __init__(self, args: Flags, project_directory: str):
        super().__init__(args)
        self.args = args
        self.project_directory = project_directory

    def run(self):
        click.echo("Creating new Morph project...")

        # Create the project structure
        if not os.path.exists(self.project_directory):
            os.makedirs(self.project_directory, exist_ok=True)
        config_file = os.path.join(self.project_directory, ProjectConfig.MORPH_YAML)
        if os.path.exists(config_file):
            click.echo(
                f"The directory is already a Morph project: {self.project_directory}"
            )
            return False
        else:
            self._create_project_structure()
            self._save_morph_yaml_template()

        # Initialize the project database
        db_manager = SqliteDBManager(self.project_directory)
        db_manager.initialize_database()

        click.echo("Project setup completed successfully.")
        self._display_post_setup_message()
        return True

    def _create_project_structure(self):
        directories = [
            ##########################################
            # Sources
            ##########################################
            f"{self.project_directory}/src",
            ##########################################
            # Outputs
            ##########################################
            f"{self.project_directory}/{ProjectConfig.OUTPUTS_DIR}",
            ##########################################
            # Knowledge
            ##########################################
            f"{self.project_directory}/knowledge",
        ]

        files = {
            ##########################################
            # Canvas
            ##########################################
            f"{self.project_directory}/src/example_python_cell.py": self._generate_example_python_cell(),
            f"{self.project_directory}/src/example_sql_cell.sql": self._generate_example_sql_cell(),
            ##########################################
            # Data
            ##########################################
            f"{self.project_directory}/data/World_Average_Temperature_2020_2024.csv": self._generate_example_data(),
            ##########################################
            # Knowledge
            ##########################################
            f"{self.project_directory}/knowledge/README.md": self._generate_knowledge_readme(),
            ##########################################
            # Project Root
            ##########################################
            f"{self.project_directory}/morph_project.sqlite3": "",
            f"{self.project_directory}/.env": self._generate_project_dotenv_content(),
            f"{self.project_directory}/.gitignore": self._generate_project_gitignore_content(),
            f"{self.project_directory}/pyproject.toml": self._generate_project_toml_content(),
            f"{self.project_directory}/README.md": self._generate_project_readme(),
        }

        # Create directories
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

        # Create files with default content
        for filepath, content in files.items():
            with open(filepath, "w") as f:
                f.write(content)

    def _display_post_setup_message(self):
        message = (
            f"\nTo activate the project environment and install dependencies, "
            f"run the following commands:\n\n"
            f"    cd {os.path.abspath(self.project_directory)}\n"
            f"    poetry install\n\n"
            f"If you don't have Poetry installed, visit https://python-poetry.org/docs/#installation "
            f"for installation instructions.\n"
        )
        click.echo(click.style(message, fg="yellow"))

    @staticmethod
    def _generate_project_readme():
        template_path = os.path.join(
            os.path.dirname(__file__), f"template/{LANG}/README.md"
        )
        with open(template_path, "r") as file:
            return file.read()

    @staticmethod
    def _generate_knowledge_readme():
        template_path = os.path.join(
            os.path.dirname(__file__), f"template/{LANG}/README_knowledge.md"
        )
        with open(template_path, "r") as file:
            return file.read()

    @staticmethod
    def _generate_example_python_cell():
        template_path = os.path.join(
            os.path.dirname(__file__), "template/cells/example_python_cell.py"
        )
        with open(template_path, "r") as file:
            return file.read()

    @staticmethod
    def _generate_example_sql_cell():
        template_path = os.path.join(
            os.path.dirname(__file__), "template/cells/example_sql_cell.sql"
        )
        with open(template_path, "r") as file:
            return file.read()

    @staticmethod
    def _generate_project_dotenv_content():
        dotenv_content = """# Environment Configuration File
# This file contains environment variables that configure the application.
# Each line in this file must be in VAR=VAL format.

# Set the TZ variable to the desired timezone.
# In Morph cloud platform, the change will take effect after the next run.
TZ=Asia/Tokyo"""
        return dotenv_content

    @staticmethod
    def _generate_project_toml_content():
        template_path = os.path.join(
            os.path.dirname(__file__), "template/pyproject.toml"
        )
        with open(template_path, "r") as file:
            return file.read()

    def _save_morph_yaml_template(self):
        morph_yaml = MorphYaml(
            version="0.1",
            resources={
                "example_python_cell": {
                    "path": OsUtils.get_abs_path(
                        "src/example_python_cell.py",
                        self.project_directory,
                    ),
                    "output_paths": [
                        OsUtils.get_abs_path(
                            "data/outputs/example_python_cell/result.csv",
                            self.project_directory,
                        )
                    ],
                },
                "example_sql_cell": {
                    "path": OsUtils.get_abs_path(
                        "src/example_sql_cell.sql", self.project_directory
                    ),
                    "output_paths": [
                        OsUtils.get_abs_path(
                            "data/outputs/example_sql_cell/result.csv",
                            self.project_directory,
                        )
                    ],
                },
            },
            canvases={
                "canvas1": {
                    "cells": {
                        "example_python_cell": {
                            "coordinates": {"x": 0, "y": 0, "w": 600, "h": 400},
                            "parents": [],
                        },
                        "example_sql_cell": {
                            "coordinates": {"x": 0, "y": 450, "w": 600, "h": 400},
                            "parents": [],
                        },
                    }
                }
            },
        )

        return morph_yaml.save_yaml(self.project_directory)

    @staticmethod
    def _generate_project_gitignore_content():
        template_path = os.path.join(os.path.dirname(__file__), "template/.gitignore")
        with open(template_path, "r") as file:
            return file.read()

    @staticmethod
    def _generate_example_data():
        template_path = os.path.join(
            os.path.dirname(__file__),
            "template/data/World_Average_Temperature_2020_2024.csv",
        )
        with open(template_path, "r") as file:
            return file.read()
