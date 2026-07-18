from datetime import date, datetime
from decimal import Decimal
from typing import Any

from connections.mysql_connection import MySQLDatabase
from connections.oracle_connection import OracleDatabase
from utils.logger import get_logger
from utils.sql_reader import SQLReader


logger = get_logger(__name__)


class SourceTargetValidator:
    """Provides reusable Oracle-to-MySQL validation methods."""

    ORACLE_SQL_FILE = (
        "sql/oracle/validation/customer_validation_queries.sql"
    )

    MYSQL_SQL_FILE = (
        "sql/mysql/validation/customer_validation_queries.sql"
    )

    def __init__(self) -> None:
        self.oracle_database = OracleDatabase()
        self.mysql_database = MySQLDatabase()

    @staticmethod
    def normalize_value(value: Any) -> Any:
        """Normalize database values for reliable comparison."""

        if isinstance(value, datetime):
            return value.date().isoformat()

        if isinstance(value, date):
            return value.isoformat()

        if isinstance(value, Decimal):
            return float(value)

        if isinstance(value, str):
            return value.strip()

        return value

    def execute_oracle_scalar(self, query_name: str) -> Any:
        query = SQLReader.read_query(
            self.ORACLE_SQL_FILE,
            query_name,
        )

        return self.oracle_database.execute_scalar(query)

    def execute_mysql_scalar(self, query_name: str) -> Any:
        query = SQLReader.read_query(
            self.MYSQL_SQL_FILE,
            query_name,
        )

        return self.mysql_database.execute_scalar(query)

    def execute_oracle_rows(
        self,
        query_name: str,
    ) -> list[dict[str, Any]]:
        query = SQLReader.read_query(
            self.ORACLE_SQL_FILE,
            query_name,
        )

        connection = self.oracle_database.connect()
        cursor = connection.cursor()

        try:
            cursor.execute(query)

            columns = [
                column[0].lower()
                for column in cursor.description
            ]

            return [
                {
                    column: self.normalize_value(value)
                    for column, value in zip(columns, row)
                }
                for row in cursor.fetchall()
            ]

        finally:
            cursor.close()
            self.oracle_database.disconnect()

    def execute_mysql_rows(
        self,
        query_name: str,
    ) -> list[dict[str, Any]]:
        query = SQLReader.read_query(
            self.MYSQL_SQL_FILE,
            query_name,
        )

        connection = self.mysql_database.connect()
        cursor = connection.cursor()

        try:
            cursor.execute(query)

            columns = [
                column[0].lower()
                for column in cursor.description
            ]

            return [
                {
                    column: self.normalize_value(value)
                    for column, value in zip(columns, row)
                }
                for row in cursor.fetchall()
            ]

        finally:
            cursor.close()
            self.mysql_database.disconnect()

    def get_source_customer_by_id(
        self,
        source_customer_id: int,
    ) -> dict[str, Any] | None:
        source_records = self.execute_oracle_rows(
            "valid_customer_records"
        )

        for record in source_records:
            if int(record["customer_id"]) == source_customer_id:
                return record

        return None

    def get_target_customer_by_source_id(
        self,
        source_customer_id: int,
    ) -> dict[str, Any] | None:
        connection = self.mysql_database.connect()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                g.golden_customer_id,
                g.first_name,
                g.last_name,
                g.full_name,
                g.email_address,
                g.phone_number,
                g.date_of_birth,
                g.gender,
                g.customer_status,
                g.source_system,
                g.source_record_count,
                x.source_customer_id,
                x.match_rule,
                x.match_score
            FROM customer_xref x
            INNER JOIN customer_golden g
                ON x.golden_customer_id =
                   g.golden_customer_id
            WHERE x.source_customer_id = %s
        """

        try:
            cursor.execute(
                query,
                (source_customer_id,),
            )

            record = cursor.fetchone()

            if record is None:
                return None

            return {
                key.lower(): self.normalize_value(value)
                for key, value in record.items()
            }

        finally:
            cursor.close()
            self.mysql_database.disconnect()

    def compare_customer_mapping(
        self,
        source_customer_id: int,
    ) -> list[str]:
        """
        Compare mapped source and target customer attributes.

        Returns a list of mismatch messages.
        """

        source_record = self.get_source_customer_by_id(
            source_customer_id
        )

        target_record = self.get_target_customer_by_source_id(
            source_customer_id
        )

        mismatches: list[str] = []

        if source_record is None:
            return [
                f"Source customer {source_customer_id} was not found."
            ]

        if target_record is None:
            return [
                f"Target customer for source ID "
                f"{source_customer_id} was not found."
            ]

        mapping = {
            "first_name": "first_name",
            "last_name": "last_name",
            "full_name": "full_name",
            "email_address": "email_address",
            "phone_number": "phone_number",
            "date_of_birth": "date_of_birth",
            "gender": "gender",
            "customer_status": "customer_status",
            "source_system": "source_system",
        }

        for source_column, target_column in mapping.items():
            source_value = self.normalize_value(
                source_record.get(source_column)
            )

            target_value = self.normalize_value(
                target_record.get(target_column)
            )

            if source_value != target_value:
                mismatches.append(
                    f"Source ID {source_customer_id}: "
                    f"{source_column}='{source_value}' does not "
                    f"match {target_column}='{target_value}'"
                )

        return mismatches