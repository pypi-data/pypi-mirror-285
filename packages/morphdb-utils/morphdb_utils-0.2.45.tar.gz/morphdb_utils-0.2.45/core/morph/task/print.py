import json

import click

from morph.cli.flags import Flags
from morph.task.base import BaseTask
from morph.task.utils.morph import MorphYaml
from morph.task.utils.sqlite import SqliteDBManager


class PrintResourceTask(BaseTask):
    def __init__(self, args: Flags):
        super().__init__(args)
        self.args = args

        self.alias = args.ALIAS
        self.path = args.PATH

        # Initialize project root
        try:
            self.project_root = MorphYaml.find_abs_project_root_dir()
        except FileNotFoundError as e:
            click.echo(click.style(str(e), fg="red"))
            raise e

        # Initialize SQLite database
        self.db_manager = SqliteDBManager(self.project_root)
        self.db_manager.initialize_database()

    def run(self):
        if self.alias:
            resource = MorphYaml.find_resource_by_alias(
                self.alias, self.project_root, self.db_manager
            )
            if resource:
                click.echo(json.dumps(resource.to_dict(), indent=2))
            else:
                click.echo(f"Alias {self.alias} not found.")
        elif self.path:
            resource = MorphYaml.find_resource_by_path(
                self.path, self.project_root, self.db_manager
            )
            if resource:
                click.echo(json.dumps(resource.to_dict(), indent=2))
            else:
                click.echo(f"Path {self.path} not found.")
        else:
            click.echo("Either --alias or --path must be provided.")
