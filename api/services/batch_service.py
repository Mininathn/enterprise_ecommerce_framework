from datetime import date, datetime
from decimal import Decimal
from typing import Any

from connections.mysql_connection import MySQLDatabase
from utils.logger import get_logger


logger = get_logger(__name__)


class BatchService:
    """Service layer for ETL batch-control operations."""

    @staticmethod
    def _normalize_value(value: Any) -> Any:
        """Convert database values into JSON-serializable values."""

        if isinstance(value, (datetime, date)):
            return value.isoformat()

        if isinstance(value, Decimal):
            return float(value)

        return value

    @staticmethod
    def _convert_row_to_dict(
        columns: list[str],
        row: tuple[Any, ...],
    ) -> dict[str, Any]:
        """Convert a database row into a normalized dictionary."""

        return {
            column: BatchService._normalize_value(value)
            for column, value in zip(columns, row)
        }

    @staticmethod
    def get_latest_batch() -> dict[str, Any] | None:
        """Return the most recently created ETL batch."""

        query = """
            SELECT *
            FROM etl_batch_control
            ORDER BY batch_id DESC
            LIMIT 1
        """

        database = MySQLDatabase()
        connection = database.connect()
        cursor = connection.cursor()

        try:
            logger.info("Retrieving the latest ETL batch.")

            cursor.execute(query)
            row = cursor.fetchone()

            if row is None:
                return None

            columns = [
                description[0]
                for description in cursor.description
            ]

            return BatchService._convert_row_to_dict(
                columns=columns,
                row=row,
            )

        finally:
            cursor.close()
            database.disconnect()

    @staticmethod
    def get_batch_by_id(
        batch_id: int,
    ) -> dict[str, Any] | None:
        """Return a specific ETL batch by its batch ID."""

        query = """
            SELECT *
            FROM etl_batch_control
            WHERE batch_id = %s
        """

        database = MySQLDatabase()
        connection = database.connect()
        cursor = connection.cursor()

        try:
            logger.info(
                "Retrieving ETL batch ID %s.",
                batch_id,
            )

            cursor.execute(
                query,
                (batch_id,),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            columns = [
                description[0]
                for description in cursor.description
            ]

            return BatchService._convert_row_to_dict(
                columns=columns,
                row=row,
            )

        finally:
            cursor.close()
            database.disconnect()

    @staticmethod
    def get_batch_history(
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Return recent ETL batch execution history."""

        query = """
            SELECT *
            FROM etl_batch_control
            ORDER BY batch_id DESC
            LIMIT %s
        """

        database = MySQLDatabase()
        connection = database.connect()
        cursor = connection.cursor()

        try:
            logger.info(
                "Retrieving ETL batch history. Limit=%s",
                limit,
            )

            cursor.execute(
                query,
                (limit,),
            )

            rows = cursor.fetchall()

            columns = [
                description[0]
                for description in cursor.description
            ]

            return [
                BatchService._convert_row_to_dict(
                    columns=columns,
                    row=row,
                )
                for row in rows
            ]

        finally:
            cursor.close()
            database.disconnect()