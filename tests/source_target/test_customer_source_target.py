from typing import Any

import pytest

from core.etl.customer_etl import CustomerETL
from core.validation.source_target_validator import (
    SourceTargetValidator,
)


@pytest.fixture(scope="module")
def completed_customer_etl() -> dict[str, int | str]:
    """Run the customer ETL once before reconciliation tests."""

    etl = CustomerETL()
    return etl.run(reset_target=True)


@pytest.fixture(scope="module")
def validator(
    completed_customer_etl: dict[str, int | str],
) -> SourceTargetValidator:
    """Provide the reusable source-to-target validator."""

    return SourceTargetValidator()


@pytest.mark.database
@pytest.mark.source_target
@pytest.mark.regression
def test_valid_source_count_matches_xref_count(
    validator: SourceTargetValidator,
) -> None:
    """
    Each valid source record must have one target XREF record.
    """

    valid_source_count = validator.execute_oracle_scalar(
        "valid_source_count"
    )

    xref_count = validator.execute_mysql_scalar(
        "xref_count"
    )

    assert valid_source_count == xref_count, (
        f"Valid Oracle source count ({valid_source_count}) "
        f"does not match MySQL XREF count ({xref_count})."
    )


@pytest.mark.database
@pytest.mark.source_target
@pytest.mark.regression
def test_distinct_source_count_matches_golden_count(
    validator: SourceTargetValidator,
) -> None:
    """
    Distinct valid source customers must equal golden records.
    """

    distinct_source_count = validator.execute_oracle_scalar(
        "distinct_valid_customer_count"
    )

    golden_count = validator.execute_mysql_scalar(
        "golden_customer_count"
    )

    assert distinct_source_count == golden_count, (
        f"Distinct valid Oracle customer count "
        f"({distinct_source_count}) does not match "
        f"MySQL golden count ({golden_count})."
    )


@pytest.mark.database
@pytest.mark.source_target
@pytest.mark.data_quality
def test_invalid_source_count_matches_rejected_count(
    validator: SourceTargetValidator,
) -> None:
    """Invalid source records must be written to rejection table."""

    invalid_source_count = validator.execute_oracle_scalar(
        "invalid_source_count"
    )

    rejected_count = validator.execute_mysql_scalar(
        "rejected_record_count"
    )

    assert invalid_source_count == rejected_count, (
        f"Invalid Oracle source count ({invalid_source_count}) "
        f"does not match rejected target count "
        f"({rejected_count})."
    )


@pytest.mark.database
@pytest.mark.source_target
@pytest.mark.transformation
@pytest.mark.parametrize(
    "source_customer_id",
    [1001, 1002, 1003],
)
def test_customer_column_level_mapping(
    validator: SourceTargetValidator,
    source_customer_id: int,
) -> None:
    """Validate source-to-target field mappings."""

    mismatches = validator.compare_customer_mapping(
        source_customer_id
    )

    assert not mismatches, "\n".join(mismatches)


@pytest.mark.database
@pytest.mark.source_target
@pytest.mark.data_quality
def test_duplicate_customer_consolidation(
    validator: SourceTargetValidator,
) -> None:
    """Duplicate source records must create one golden record."""

    duplicate_groups = validator.execute_oracle_rows(
        "duplicate_customer_groups"
    )

    target_records = validator.execute_mysql_rows(
        "golden_customer_records"
    )

    target_lookup = {
        (
            record["email_address"],
            record["phone_number"],
        ): record
        for record in target_records
    }

    mismatches: list[str] = []

    for duplicate_group in duplicate_groups:
        match_key = (
            duplicate_group["email_address"],
            duplicate_group["phone_number"],
        )

        target_record = target_lookup.get(match_key)

        if target_record is None:
            mismatches.append(
                f"Golden record was not found for "
                f"duplicate group {match_key}."
            )

            continue

        expected_count = int(
            duplicate_group["source_record_count"]
        )

        actual_count = int(
            target_record["source_record_count"]
        )

        if expected_count != actual_count:
            mismatches.append(
                f"Duplicate group {match_key}: expected "
                f"source_record_count={expected_count}, "
                f"but found {actual_count}."
            )

    assert not mismatches, "\n".join(mismatches)


@pytest.mark.database
@pytest.mark.source_target
@pytest.mark.data_quality
def test_rejected_source_ids_reconciled(
    validator: SourceTargetValidator,
) -> None:
    """Rejected Oracle IDs must match MySQL rejection IDs."""

    invalid_source_records = validator.execute_oracle_rows(
        "invalid_customer_records"
    )

    rejected_target_records = validator.execute_mysql_rows(
        "rejected_source_ids"
    )

    source_rejected_ids = {
        str(record["customer_id"])
        for record in invalid_source_records
    }

    target_rejected_ids = {
        str(record["source_record_id"])
        for record in rejected_target_records
    }

    assert source_rejected_ids == target_rejected_ids, (
        f"Rejected ID mismatch. "
        f"Oracle={source_rejected_ids}, "
        f"MySQL={target_rejected_ids}"
    )


@pytest.mark.database
@pytest.mark.source_target
@pytest.mark.data_quality
def test_no_duplicate_golden_customers(
    validator: SourceTargetValidator,
) -> None:
    """Golden table must not contain duplicate match keys."""

    duplicate_records = validator.execute_mysql_rows(
        "duplicate_golden_records"
    )

    assert duplicate_records == [], (
        f"Duplicate golden customer records found: "
        f"{duplicate_records}"
    )


@pytest.mark.database
@pytest.mark.source_target
@pytest.mark.data_quality
def test_no_orphan_customer_xrefs(
    validator: SourceTargetValidator,
) -> None:
    """Every XREF must reference a valid golden customer."""

    orphan_records = validator.execute_mysql_rows(
        "orphan_xref_records"
    )

    assert orphan_records == [], (
        f"Orphan customer XREF records found: {orphan_records}"
    )


@pytest.mark.database
@pytest.mark.source_target
@pytest.mark.data_quality
def test_no_orphan_customer_addresses(
    validator: SourceTargetValidator,
) -> None:
    """Every target address must reference a golden customer."""

    orphan_records = validator.execute_mysql_rows(
        "orphan_address_records"
    )

    assert orphan_records == [], (
        f"Orphan customer-address records found: "
        f"{orphan_records}"
    )


@pytest.mark.database
@pytest.mark.source_target
@pytest.mark.regression
def test_latest_batch_count_reconciliation(
    validator: SourceTargetValidator,
) -> None:
    """Verify counts stored in the latest ETL batch record."""

    latest_batch_records = validator.execute_mysql_rows(
        "latest_batch_record"
    )

    assert len(latest_batch_records) == 1, (
        "Latest ETL batch-control record was not found."
    )

    batch = latest_batch_records[0]

    total_source_count = validator.execute_oracle_scalar(
        "total_source_count"
    )

    golden_count = validator.execute_mysql_scalar(
        "golden_customer_count"
    )

    rejected_count = validator.execute_mysql_scalar(
        "rejected_record_count"
    )

    assert batch["batch_status"] == "COMPLETED"

    assert int(batch["source_count"]) == int(
        total_source_count
    )

    assert int(batch["target_count"]) == int(
        golden_count
    )

    assert int(batch["rejected_count"]) == int(
        rejected_count
    )