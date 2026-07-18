import pytest

from connections.mysql_connection import MySQLDatabase
from connections.oracle_connection import OracleDatabase


@pytest.mark.database
@pytest.mark.oracle
@pytest.mark.smoke
def test_oracle_customer_source_tables_exist() -> None:
    database = OracleDatabase()
    connection = database.connect()
    cursor = connection.cursor()

    expected_tables = {
        "SRC_CUSTOMER",
        "SRC_CUSTOMER_ADDRESS",
    }

    try:
        cursor.execute(
            """
            SELECT TABLE_NAME
            FROM USER_TABLES
            WHERE TABLE_NAME IN (
                'SRC_CUSTOMER',
                'SRC_CUSTOMER_ADDRESS'
            )
            """
        )

        actual_tables = {row[0] for row in cursor.fetchall()}

        assert actual_tables == expected_tables, (
            f"Expected Oracle tables {expected_tables}, "
            f"but found {actual_tables}"
        )

    finally:
        cursor.close()
        database.disconnect()


@pytest.mark.database
@pytest.mark.mysql
@pytest.mark.smoke
def test_mysql_customer_target_tables_exist() -> None:
    database = MySQLDatabase()
    connection = database.connect()
    cursor = connection.cursor()

    expected_tables = {
        "customer_golden",
        "customer_address",
        "customer_xref",
        "etl_batch_control",
        "etl_rejected_record",
    }

    try:
        cursor.execute(
            """
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
            """
        )

        actual_tables = {row[0] for row in cursor.fetchall()}

        missing_tables = expected_tables - actual_tables

        assert not missing_tables, (
            f"Missing MySQL target tables: {missing_tables}"
        )

    finally:
        cursor.close()
        database.disconnect()


@pytest.mark.database
@pytest.mark.oracle
def test_oracle_customer_source_count() -> None:
    database = OracleDatabase()

    actual_count = database.execute_scalar(
        "SELECT COUNT(*) FROM SRC_CUSTOMER"
    )

    assert actual_count == 5, (
        f"Expected 5 Oracle source customers, "
        f"but found {actual_count}"
    )