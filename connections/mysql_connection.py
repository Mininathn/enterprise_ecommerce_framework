from typing import Any

import mysql.connector
from mysql.connector import Error
from mysql.connector.connection import MySQLConnection

from utils.config_reader import ConfigReader
from utils.logger import get_logger


logger = get_logger(__name__)


class MySQLDatabase:
    """Manages connections to the MySQL target database."""

    def __init__(self) -> None:
        self.config = ConfigReader().get_mysql_config()
        self.connection: MySQLConnection | None = None

    def connect(self) -> MySQLConnection:
        """Open and return a MySQL database connection."""

        try:
            logger.info(
                "Connecting to MySQL database '%s' on %s:%s",
                self.config["database"],
                self.config["host"],
                self.config["port"],
            )

            self.connection = mysql.connector.connect(
                host=self.config["host"],
                port=self.config["port"],
                database=self.config["database"],
                user=self.config["user"],
                password=self.config["password"],
                connection_timeout=10,
            )

            if not self.connection.is_connected():
                raise ConnectionError(
                    "MySQL connector returned a disconnected connection."
                )

            logger.info("MySQL connection established successfully.")
            return self.connection

        except Error as error:
            logger.exception("MySQL connection failed: %s", error)
            raise ConnectionError(
                f"Unable to connect to MySQL: {error}"
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
        """Close the active MySQL database connection."""

        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL connection closed.")

        self.connection = None