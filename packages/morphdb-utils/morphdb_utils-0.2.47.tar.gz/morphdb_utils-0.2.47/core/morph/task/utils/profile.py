import os
from dataclasses import dataclass
from typing import Any, Dict, Literal, Union

import yaml

from morph.task.constant.project_config import ProjectConfig

CONNECTION_TYPE = Union[
    Literal["postgresql"],
    Literal["mysql"],
    Literal["redshift"],
    Literal["snowflake_user_password"],
    Literal["snowflake_oauth"],
    Literal["bigquery_oauth"],
    Literal["bigquery_service_account"],
    Literal["bigquery_service_account_json"],
]


@dataclass
class PostgresqlConnection:
    type: Literal["postgresql"]
    host: str
    user: str
    password: str
    port: int
    dbname: str
    schema: str


@dataclass
class MysqlConnection:
    type: Literal["mysql"]
    host: str
    user: str
    password: str
    port: int
    dbname: str


@dataclass
class RedshiftConnection:
    type: Literal["redshift"]
    host: str
    user: str
    password: str
    port: int
    dbname: str
    schema: str


@dataclass
class SnowflakeConnectionUserPassword:
    type: Literal["snowflake"]
    method: Literal["user_password"]
    account: str
    database: str
    user: str
    password: str
    role: str
    schema: str
    warehouse: str


@dataclass
class SnowflakeConnectionOAuth:
    type: Literal["snowflake"]
    method: Literal["oauth"]
    account: str
    database: str
    refresh_token: str
    client_id: str
    client_secret: str
    redirect_uri: str
    role: str
    schema: str
    warehouse: str


@dataclass
class BigqueryConnectionOAuth:
    type: Literal["bigquery"]
    method: Literal["oauth"]
    project: str
    dataset: str
    refresh_token: str
    client_id: str
    client_secret: str
    redirect_uri: str


@dataclass
class BigqueryConnectionServiceAccount:
    type: Literal["bigquery"]
    method: Literal["service_account"]
    project: str
    dataset: str
    keyfile: str


@dataclass
class BigqueryConnectionServiceAccountJsonKeyFile:
    type: str
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_x509_cert_url: str


@dataclass
class BigqueryConnectionServiceAccountJson:
    type: Literal["bigquery"]
    method: Literal["service_account_json"]
    project: str
    dataset: str
    keyfile_json: BigqueryConnectionServiceAccountJsonKeyFile


@dataclass
class ProfileYaml:
    """
    connections:
        slug:
            each connection info...
    """

    connections: Dict[
        str,
        Union[
            PostgresqlConnection,
            MysqlConnection,
            RedshiftConnection,
            SnowflakeConnectionUserPassword,
            SnowflakeConnectionOAuth,
            BigqueryConnectionOAuth,
            BigqueryConnectionServiceAccount,
            BigqueryConnectionServiceAccountJson,
        ],
    ]

    @staticmethod
    def from_dict(data: dict) -> "ProfileYaml":
        connections = {
            slug: connection_info
            for slug, connection_info in data.get("connections", {}).items()
        }
        return ProfileYaml(connections=connections)

    @staticmethod
    def load_yaml() -> "ProfileYaml":
        profile_yaml_path = ProjectConfig.MORPH_PROFILE_PATH
        if not os.path.isfile(profile_yaml_path):
            raise FileNotFoundError(f"profiles.yaml not found in {profile_yaml_path}")

        with open(profile_yaml_path, "r") as file:
            data = yaml.safe_load(file)

        return ProfileYaml.from_dict(data)

    @staticmethod
    def get_connection_type(connection: dict) -> CONNECTION_TYPE:
        if connection.get("type", "") == "postgresql":
            return "postgresql"
        elif connection.get("type", "") == "mysql":
            return "mysql"
        elif connection.get("type", "") == "redshift":
            return "redshift"
        elif (
            connection.get("type", "") == "snowflake"
            and connection.get("method", "") == "user_password"
        ):
            return "snowflake_user_password"
        elif (
            connection.get("type", "") == "snowflake"
            and connection.get("method", "") == "oauth"
        ):
            return "snowflake_oauth"
        elif (
            connection.get("type", "") == "bigquery"
            and connection.get("method", "") == "oauth"
        ):
            return "bigquery_oauth"
        elif (
            connection.get("type", "") == "bigquery"
            and connection.get("method", "") == "service_account"
        ):
            return "bigquery_service_account"
        elif (
            connection.get("type", "") == "bigquery"
            and connection.get("method", "") == "service_account_json"
        ):
            return "bigquery_service_account_json"
        else:
            raise ValueError(f"Unsupported connection type: {connection}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "connections": self.connections,
        }
