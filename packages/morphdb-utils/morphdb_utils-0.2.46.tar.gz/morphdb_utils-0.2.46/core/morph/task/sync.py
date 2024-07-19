import click

from morph.cli.flags import Flags
from morph.task.base import BaseTask
from morph.task.utils.morph import MorphYaml
from morph.task.utils.sqlite import SqliteDBManager


class SyncTask(BaseTask):
    def __init__(self, args: Flags):
        super().__init__(args)
        self.args = args

        try:
            self.project_root = MorphYaml.find_abs_project_root_dir()
        except FileNotFoundError as e:
            click.echo(click.style(str(e), fg="red"))
            raise e

        self.db_manager = SqliteDBManager(self.project_root)
        self.db_manager.initialize_database()

    def run(self) -> None:
        self.db_manager.sync_resources_from_yaml()
        click.echo(click.style("Synced morph.yaml to SQLite database.", fg="green"))
