import json
import re
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from connections.mysql_connection import MySQLDatabase
from connections.oracle_connection import OracleDatabase
from utils.logger import get_logger


logger = get_logger(__name__)


class CustomerETL:
    """Extracts customer data from Oracle and loads it into MySQL."""

    EMAIL_PATTERN = re.compile(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )

    def __init__(self) -> None:
        self.oracle_database = OracleDatabase()
        self.mysql_database = MySQLDatabase()

        self.oracle_connection = None
        self.mysql_connection = None

        self.batch_id: int | None = None

    @staticmethod
    def serialize_value(value: Any) -> Any:
        """Convert non-JSON-compatible database values."""

        if isinstance(value, (datetime, date)):
            return value.isoformat()

        if isinstance(value, Decimal):
            return float(value)

        return value

    def serialize_record(self, record: dict[str, Any]) -> str:
        """Serialize a source record for the rejection table."""

        serializable_record = {
            key: self.serialize_value(value)
            for key, value in record.items()
        }

        return json.dumps(serializable_record)

    def extract_customers(self) -> list[dict[str, Any]]:
        """Extract customer records from the Oracle source."""

        logger.info("Starting customer extraction from Oracle.")

        cursor = self.oracle_connection.cursor()

        query = """
            SELECT
                CUSTOMER_ID,
                SOURCE_SYSTEM,
                FIRST_NAME,
                LAST_NAME,
                EMAIL_ADDRESS,
                PHONE_NUMBER,
                DATE_OF_BIRTH,
                GENDER,
                CUSTOMER_STATUS,
                CREATED_DATE,
                UPDATED_DATE,
                ETL_STATUS
            FROM SRC_CUSTOMER
            ORDER BY CUSTOMER_ID
        """

        try:
            cursor.execute(query)

            column_names = [
                column[0].lower()
                for column in cursor.description
            ]

            records = [
                dict(zip(column_names, row))
                for row in cursor.fetchall()
            ]

            logger.info(
                "Extracted %s customer records from Oracle.",
                len(records),
            )

            return records

        finally:
            cursor.close()

    def validate_customer(
        self,
        customer: dict[str, Any],
    ) -> list[str]:
        """Return validation errors for a source customer."""

        validation_errors: list[str] = []

        customer_id = customer.get("customer_id")
        first_name = customer.get("first_name")
        last_name = customer.get("last_name")
        email_address = customer.get("email_address")
        phone_number = customer.get("phone_number")

        if customer_id is None:
            validation_errors.append("Customer ID is missing")

        if not first_name or not str(first_name).strip():
            validation_errors.append("First name is missing")

        if not last_name or not str(last_name).strip():
            validation_errors.append("Last name is missing")

        if not email_address:
            validation_errors.append("Email address is missing")
        elif not self.EMAIL_PATTERN.fullmatch(
            str(email_address).strip()
        ):
            validation_errors.append("Invalid email address")

        if not phone_number:
            validation_errors.append("Phone number is missing")
        elif not str(phone_number).strip().isdigit():
            validation_errors.append(
                "Phone number must contain digits only"
            )
        elif len(str(phone_number).strip()) != 10:
            validation_errors.append(
                "Phone number must contain exactly 10 digits"
            )

        return validation_errors

    @staticmethod
    def normalize_customer(
        customer: dict[str, Any],
    ) -> dict[str, Any]:
        """Normalize customer attributes before matching and loading."""

        normalized_customer = customer.copy()

        normalized_customer["first_name"] = (
            str(customer["first_name"]).strip().title()
        )

        normalized_customer["last_name"] = (
            str(customer["last_name"]).strip().title()
        )

        normalized_customer["email_address"] = (
            str(customer["email_address"]).strip().lower()
        )

        normalized_customer["phone_number"] = (
            str(customer["phone_number"]).strip()
        )

        normalized_customer["customer_status"] = (
            str(
                customer.get("customer_status") or "ACTIVE"
            )
            .strip()
            .upper()
        )

        normalized_customer["source_system"] = (
            str(
                customer.get("source_system") or "ORACLE_ECOM"
            )
            .strip()
            .upper()
        )

        if normalized_customer.get("gender"):
            normalized_customer["gender"] = (
                str(normalized_customer["gender"])
                .strip()
                .upper()
            )

        return normalized_customer

    @staticmethod
    def get_match_key(
        customer: dict[str, Any],
    ) -> tuple[str, str]:
        """Create a deterministic duplicate-matching key."""

        return (
            customer["email_address"],
            customer["phone_number"],
        )

    def split_valid_and_rejected(
        self,
        customers: list[dict[str, Any]],
    ) -> tuple[
        list[dict[str, Any]],
        list[tuple[dict[str, Any], str]],
    ]:
        """Separate valid records from rejected records."""

        valid_customers: list[dict[str, Any]] = []
        rejected_customers: list[
            tuple[dict[str, Any], str]
        ] = []

        for customer in customers:
            validation_errors = self.validate_customer(customer)

            if validation_errors:
                rejection_reason = "; ".join(validation_errors)

                rejected_customers.append(
                    (customer, rejection_reason)
                )

                logger.warning(
                    "Rejecting customer ID %s: %s",
                    customer.get("customer_id"),
                    rejection_reason,
                )

                continue

            valid_customers.append(
                self.normalize_customer(customer)
            )

        logger.info(
            "Customer validation completed. Valid=%s, Rejected=%s",
            len(valid_customers),
            len(rejected_customers),
        )

        return valid_customers, rejected_customers

    def group_duplicate_customers(
        self,
        customers: list[dict[str, Any]],
    ) -> list[list[dict[str, Any]]]:
        """Group customers by normalized email and phone."""

        grouped_customers: dict[
            tuple[str, str],
            list[dict[str, Any]],
        ] = defaultdict(list)

        for customer in customers:
            match_key = self.get_match_key(customer)
            grouped_customers[match_key].append(customer)

        customer_groups = list(grouped_customers.values())

        logger.info(
            "Duplicate matching completed. Golden groups=%s",
            len(customer_groups),
        )

        return customer_groups

    def create_batch(self, source_count: int) -> int:
        """Create the ETL batch-control record."""

        cursor = self.mysql_connection.cursor()

        query = """
            INSERT INTO etl_batch_control (
                batch_name,
                source_system,
                target_system,
                batch_status,
                source_count
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """

        try:
            cursor.execute(
                query,
                (
                    "CUSTOMER_ORACLE_TO_MYSQL",
                    "ORACLE_ECOM",
                    "MYSQL_ECOM",
                    "STARTED",
                    source_count,
                ),
            )

            self.batch_id = cursor.lastrowid

            if self.batch_id is None:
                raise RuntimeError(
                    "MySQL did not return an ETL batch ID."
                )

            logger.info(
                "ETL batch created successfully. Batch ID=%s",
                self.batch_id,
            )

            return int(self.batch_id)

        finally:
            cursor.close()

    def insert_golden_customer(
        self,
        customer_group: list[dict[str, Any]],
    ) -> int:
        """Insert one golden record for a duplicate group."""

        master_customer = customer_group[0]

        first_name = master_customer["first_name"]
        last_name = master_customer["last_name"]
        full_name = f"{first_name} {last_name}".strip()

        cursor = self.mysql_connection.cursor()

        query = """
            INSERT INTO customer_golden (
                first_name,
                last_name,
                full_name,
                email_address,
                phone_number,
                date_of_birth,
                gender,
                customer_status,
                source_system,
                source_record_count
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """

        try:
            cursor.execute(
                query,
                (
                    first_name,
                    last_name,
                    full_name,
                    master_customer["email_address"],
                    master_customer["phone_number"],
                    master_customer.get("date_of_birth"),
                    master_customer.get("gender"),
                    master_customer["customer_status"],
                    master_customer["source_system"],
                    len(customer_group),
                ),
            )

            golden_customer_id = cursor.lastrowid

            if golden_customer_id is None:
                raise RuntimeError(
                    "MySQL did not return a golden customer ID."
                )

            logger.info(
                "Golden customer created. "
                "Golden ID=%s, source records=%s",
                golden_customer_id,
                len(customer_group),
            )

            return int(golden_customer_id)

        finally:
            cursor.close()

    def insert_customer_xrefs(
        self,
        golden_customer_id: int,
        customer_group: list[dict[str, Any]],
    ) -> int:
        """Insert source-to-golden cross-reference records."""

        cursor = self.mysql_connection.cursor()

        query = """
            INSERT INTO customer_xref (
                golden_customer_id,
                source_customer_id,
                source_system,
                match_rule,
                match_score
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """

        inserted_count = 0

        try:
            for customer in customer_group:
                cursor.execute(
                    query,
                    (
                        golden_customer_id,
                        customer["customer_id"],
                        customer["source_system"],
                        "EXACT_EMAIL_AND_PHONE",
                        Decimal("100.00"),
                    ),
                )

                inserted_count += 1

            return inserted_count

        finally:
            cursor.close()

    def insert_rejected_customer(
        self,
        customer: dict[str, Any],
        rejection_reason: str,
    ) -> None:
        """Write one rejected customer to the rejection table."""

        cursor = self.mysql_connection.cursor()

        query = """
            INSERT INTO etl_rejected_record (
                batch_id,
                source_table,
                source_record_id,
                rejection_reason,
                rejected_payload
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """

        try:
            cursor.execute(
                query,
                (
                    self.batch_id,
                    "SRC_CUSTOMER",
                    str(customer.get("customer_id")),
                    rejection_reason,
                    self.serialize_record(customer),
                ),
            )

        finally:
            cursor.close()

    def update_batch_status(
        self,
        status: str,
        target_count: int = 0,
        rejected_count: int = 0,
        error_message: str | None = None,
    ) -> None:
        """Update the current batch-control record."""

        if self.batch_id is None:
            return

        cursor = self.mysql_connection.cursor()

        query = """
            UPDATE etl_batch_control
            SET
                batch_status = %s,
                target_count = %s,
                rejected_count = %s,
                completed_at = CURRENT_TIMESTAMP,
                error_message = %s
            WHERE batch_id = %s
        """

        try:
            cursor.execute(
                query,
                (
                    status,
                    target_count,
                    rejected_count,
                    error_message,
                    self.batch_id,
                ),
            )

        finally:
            cursor.close()

    def clear_target_data(self) -> None:
        """Clear target data to make local ETL runs repeatable."""

        logger.info("Clearing existing customer target data.")

        cursor = self.mysql_connection.cursor()

        statements = [
            "DELETE FROM etl_rejected_record",
            "DELETE FROM customer_xref",
            "DELETE FROM customer_address",
            "DELETE FROM customer_golden",
            "DELETE FROM etl_batch_control",
        ]

        try:
            for statement in statements:
                cursor.execute(statement)

            self.mysql_connection.commit()

            logger.info("Existing customer target data cleared.")

        finally:
            cursor.close()

    def run(self, reset_target: bool = True) -> dict[str, int | str]:
        """Execute the complete customer ETL pipeline."""

        source_count = 0
        golden_count = 0
        xref_count = 0
        rejected_count = 0

        try:
            self.oracle_connection = (
                self.oracle_database.connect()
            )

            self.mysql_connection = (
                self.mysql_database.connect()
            )

            if reset_target:
                self.clear_target_data()

            source_customers = self.extract_customers()
            source_count = len(source_customers)

            self.create_batch(source_count)

            valid_customers, rejected_customers = (
                self.split_valid_and_rejected(
                    source_customers
                )
            )

            customer_groups = self.group_duplicate_customers(
                valid_customers
            )

            for customer_group in customer_groups:
                golden_customer_id = (
                    self.insert_golden_customer(
                        customer_group
                    )
                )

                golden_count += 1

                xref_count += self.insert_customer_xrefs(
                    golden_customer_id,
                    customer_group,
                )

            for customer, rejection_reason in rejected_customers:
                self.insert_rejected_customer(
                    customer,
                    rejection_reason,
                )

                rejected_count += 1

            self.update_batch_status(
                status="COMPLETED",
                target_count=golden_count,
                rejected_count=rejected_count,
            )

            self.mysql_connection.commit()

            result: dict[str, int | str] = {
                "batch_id": self.batch_id or 0,
                "batch_status": "COMPLETED",
                "source_count": source_count,
                "golden_count": golden_count,
                "xref_count": xref_count,
                "rejected_count": rejected_count,
            }

            logger.info(
                "Customer ETL completed successfully: %s",
                result,
            )

            return result

        except Exception as error:
            logger.exception(
                "Customer ETL failed: %s",
                error,
            )

            if self.mysql_connection is not None:
                self.mysql_connection.rollback()

                try:
                    self.update_batch_status(
                        status="FAILED",
                        target_count=golden_count,
                        rejected_count=rejected_count,
                        error_message=str(error)[:1000],
                    )

                    self.mysql_connection.commit()

                except Exception:
                    self.mysql_connection.rollback()

            raise

        finally:
            if self.oracle_connection is not None:
                self.oracle_database.disconnect()

            if self.mysql_connection is not None:
                self.mysql_database.disconnect()