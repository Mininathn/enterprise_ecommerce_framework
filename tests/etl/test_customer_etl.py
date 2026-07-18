import pytest

from connections.mysql_connection import MySQLDatabase
from core.etl.customer_etl import CustomerETL


@pytest.fixture(scope="module")
def customer_etl_result() -> dict[str, int | str]:
    """Run the customer ETL once for this test module."""

    etl = CustomerETL()
    return etl.run(reset_target=True)


@pytest.mark.database
@pytest.mark.source_target
@pytest.mark.regression
def test_customer_etl_summary(
    customer_etl_result: dict[str, int | str],
) -> None:
    """Validate the summary returned by the ETL process."""

    assert customer_etl_result["batch_status"] == "COMPLETED"
    assert customer_etl_result["source_count"] == 5
    assert customer_etl_result["golden_count"] == 3
    assert customer_etl_result["xref_count"] == 4
    assert customer_etl_result["rejected_count"] == 1


@pytest.mark.database
@pytest.mark.mysql
@pytest.mark.source_target
def test_customer_golden_count(
    customer_etl_result: dict[str, int | str],
) -> None:
    """Validate the number of golden customer records."""

    database = MySQLDatabase()

    actual_count = database.execute_scalar(
        "SELECT COUNT(*) FROM customer_golden"
    )

    assert actual_count == 3, (
        f"Expected 3 golden customers, "
        f"but found {actual_count}"
    )


@pytest.mark.database
@pytest.mark.mysql
@pytest.mark.source_target
def test_customer_xref_count(
    customer_etl_result: dict[str, int | str],
) -> None:
    """Validate source-to-golden cross-reference count."""

    database = MySQLDatabase()

    actual_count = database.execute_scalar(
        "SELECT COUNT(*) FROM customer_xref"
    )

    assert actual_count == 4, (
        f"Expected 4 customer cross-reference records, "
        f"but found {actual_count}"
    )


@pytest.mark.database
@pytest.mark.mysql
@pytest.mark.data_quality
def test_rejected_customer_count(
    customer_etl_result: dict[str, int | str],
) -> None:
    """Validate invalid customer rejection count."""

    database = MySQLDatabase()

    actual_count = database.execute_scalar(
        "SELECT COUNT(*) FROM etl_rejected_record"
    )

    assert actual_count == 1, (
        f"Expected 1 rejected customer, "
        f"but found {actual_count}"
    )


@pytest.mark.database
@pytest.mark.mysql
@pytest.mark.data_quality
def test_duplicate_customers_merged(
    customer_etl_result: dict[str, int | str],
) -> None:
    """Verify duplicate source customers produce one golden record."""

    database = MySQLDatabase()
    connection = database.connect()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                source_record_count
            FROM customer_golden
            WHERE email_address = %s
              AND phone_number = %s
            """,
            (
                "mininath.navdkar@example.com",
                "9876543210",
            ),
        )

        result = cursor.fetchone()

        assert result is not None, (
            "Expected duplicate golden customer was not found."
        )

        assert result[0] == 2, (
            f"Expected source_record_count=2, "
            f"but found {result[0]}"
        )

    finally:
        cursor.close()
        database.disconnect()


@pytest.mark.database
@pytest.mark.mysql
@pytest.mark.transformation
def test_customer_full_name_transformation(
    customer_etl_result: dict[str, int | str],
) -> None:
    """Verify first and last names are combined correctly."""

    database = MySQLDatabase()
    connection = database.connect()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                first_name,
                last_name,
                full_name
            FROM customer_golden
            WHERE email_address = %s
            """,
            ("priya.sharma@example.com",),
        )

        result = cursor.fetchone()

        assert result is not None, (
            "Priya Sharma golden customer was not found."
        )

        first_name, last_name, full_name = result

        assert full_name == f"{first_name} {last_name}"

    finally:
        cursor.close()
        database.disconnect()


@pytest.mark.database
@pytest.mark.mysql
@pytest.mark.data_quality
def test_invalid_email_rejection_reason(
    customer_etl_result: dict[str, int | str],
) -> None:
    """Verify the invalid email record has the correct reason."""

    database = MySQLDatabase()
    connection = database.connect()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                source_record_id,
                rejection_reason
            FROM etl_rejected_record
            WHERE source_record_id = %s
            """,
            ("1005",),
        )

        result = cursor.fetchone()

        assert result is not None, (
            "Rejected source customer 1005 was not found."
        )

        source_record_id, rejection_reason = result

        assert source_record_id == "1005"
        assert "Invalid email address" in rejection_reason

    finally:
        cursor.close()
        database.disconnect()


@pytest.mark.database
@pytest.mark.mysql
@pytest.mark.source_target
def test_completed_batch_control_record(
    customer_etl_result: dict[str, int | str],
) -> None:
    """Verify ETL batch counts and final status."""

    batch_id = customer_etl_result["batch_id"]

    database = MySQLDatabase()
    connection = database.connect()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                batch_status,
                source_count,
                target_count,
                rejected_count
            FROM etl_batch_control
            WHERE batch_id = %s
            """,
            (batch_id,),
        )

        result = cursor.fetchone()

        assert result is not None, (
            f"Batch-control record {batch_id} was not found."
        )

        (
            batch_status,
            source_count,
            target_count,
            rejected_count,
        ) = result

        assert batch_status == "COMPLETED"
        assert source_count == 5
        assert target_count == 3
        assert rejected_count == 1

    finally:
        cursor.close()
        database.disconnect()