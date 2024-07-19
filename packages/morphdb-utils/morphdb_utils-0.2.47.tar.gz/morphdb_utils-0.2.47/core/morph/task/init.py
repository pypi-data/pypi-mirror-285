import configparser
import os
import socket

import click

from morph.task.base import BaseTask
from morph.task.constant.project_config import ProjectConfig


class InitTask(BaseTask):
    def run(self):
        # Verify network connectivity
        if not self.check_network_connection():
            click.echo("No network connection. Please check your internet settings.")
            return False
        else:
            click.echo("Initializing Morph CLI...")

        # Check if the .morph directory exists in the user's home directory; create it if not
        morph_dir = ProjectConfig.INIT_DIR
        if not os.path.exists(morph_dir):
            os.makedirs(morph_dir)
            click.echo(f"Created directory at {morph_dir}")

        # Request configuration settings from the user
        team_slug = input("Enter your team slug: ")
        app_url = input("Enter your application URL: ")
        database_id = input("Enter your database ID: ")
        api_key = input("Enter your API key: ")

        if not team_slug:
            click.echo("Error: Team slug is required.")
            return False
        if not app_url:
            click.echo("Error: Application URL is required.")
            return False
        if not database_id:
            click.echo("Error: Database ID is required.")
            return False
        if not api_key:
            click.echo("Error: API key is required.")
            return False

        # Load existing file or create new one if it doesn't exist
        config = configparser.ConfigParser()
        cred_file = os.path.join(morph_dir, "credentials")
        if os.path.exists(cred_file):
            config.read(cred_file)

        # Update the settings in the specific section
        if not config.has_section("default"):
            click.echo("Creating new credentials...")
        else:
            click.echo(
                f"Credentials for team ({team_slug}) already exists. Updating..."
            )
        config["default"] = {
            "team_slug": team_slug,
            "app_url": app_url,
            "database_id": database_id,
            "api_key": api_key,
        }

        # Write the updated profile back to the file
        with open(cred_file, "w") as file:
            config.write(file)

        click.echo(f"Credentials saved to {cred_file}")
        return True

    @staticmethod
    def check_network_connection():
        try:
            # Attempt to connect to Cloudflare DNS server on port 53
            socket.create_connection(("1.1.1.1", 53), timeout=10)
            return True
        except OSError:
            return False
