import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"
CONFIG_FILE = PROJECT_ROOT / "config" / "config.yaml"

load_dotenv(ENV_FILE)


class ConfigReader:
    """Loads framework configuration from YAML and environment variables."""

    def __init__(self, config_file: Path = CONFIG_FILE) -> None:
        if not config_file.exists():
            raise FileNotFoundError(
                f"Configuration file was not found: {config_file}"
            )

        with config_file.open("r", encoding="utf-8") as file:
            self._config: dict[str, Any] = yaml.safe_load(file) or {}

    def get(self, *keys: str, default: Any = None) -> Any:
        value: Any = self._config

        for key in keys:
            if not isinstance(value, dict) or key not in value:
                return default
            value = value[key]

        return value

    @staticmethod
    def get_required_env(variable_name: str) -> str:
        value = os.getenv(variable_name)

        if value is None or not value.strip():
            raise ValueError(
                f"Required environment variable is missing: {variable_name}"
            )

        return value.strip()

    def get_mysql_config(self) -> dict[str, Any]:
        mysql_config = self.get("databases", "mysql")

        if not isinstance(mysql_config, dict):
            raise ValueError(
                "MySQL configuration is missing from config.yaml"
            )

        return {
            "host": self.get_required_env(mysql_config["host_env"]),
            "port": int(self.get_required_env(mysql_config["port_env"])),
            "database": self.get_required_env(mysql_config["database_env"]),
            "user": self.get_required_env(mysql_config["username_env"]),
            "password": self.get_required_env(mysql_config["password_env"]),
        }

    def get_oracle_config(self) -> dict[str, Any]:
        oracle_config = self.get("databases", "oracle")

        if not isinstance(oracle_config, dict):
            raise ValueError(
                "Oracle configuration is missing from config.yaml"
            )

        return {
            "host": self.get_required_env(oracle_config["host_env"]),
            "port": int(self.get_required_env(oracle_config["port_env"])),
            "sid": self.get_required_env(oracle_config["sid_env"]),
            "user": self.get_required_env(oracle_config["username_env"]),
            "password": self.get_required_env(oracle_config["password_env"]),
        }