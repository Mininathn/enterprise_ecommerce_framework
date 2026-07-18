from typing import Any

import oracledb

from utils.config_reader import ConfigReader
from utils.logger import get_logger


logger = get_logger(__name__)


class OracleDatabase:
    """Manages connections to the Oracle source database."""

    def __init__(self) -> None:
        self.config = ConfigReader().get_oracle_config()
        self.connection: oracledb.Connection | None = None

    def connect(self) -> oracledb.Connection:
        """Open and return an Oracle database connection."""

        try:
            dsn = oracledb.makedsn(
                host=self.config["host"],
                port=self.config["port"],
                sid=self.config["sid"],
            )

            logger.info(
                "Connecting to Oracle SID '%s' on %s:%s",
                self.config["sid"],
                self.config["host"],
                self.config["port"],
            )

            self.connection = oracledb.connect(
                user=self.config["user"],
                password=self.config["password"],
                dsn=dsn,
            )

            logger.info(
                "Oracle connection established successfully."
            )

            return self.connection

        except oracledb.Error as error:
            logger.exception(
                "Oracle connection failed: %s",
                error,
            )

            raise ConnectionError(
                f"Unable to connect to Oracle: {error}"
            ) from error

    def execute_scalar(self, query: str) -> Any:
        """Execute a query that returns one value."""

        connection = self.connect()
        cursor = connection.cursor()

        try:
            cursor.execute(query)
            result = cursor.fetchone()

            if result is None:
                return None

            return result[0]

        finally:
            cursor.close()
            self.disconnect()

    def disconnect(self) -> None:
        """Close the active Oracle connection."""

        if self.connection is not None:
            self.connection.close()
            logger.info("Oracle connection closed.")

        self.connection = None