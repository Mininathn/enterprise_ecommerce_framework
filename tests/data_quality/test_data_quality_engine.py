import json
from pathlib import Path
from typing import Any

import pytest

from core.etl.customer_etl import CustomerETL
from core.validation.data_quality_engine import (
    DataQualityEngine,
)


@pytest.fixture(scope="module")
def completed_customer_etl() -> dict[str, int | str]:
    """Load fresh Oracle customer data into MySQL."""

    etl = CustomerETL()
    return etl.run(reset_target=True)


@pytest.fixture(scope="module")
def data_quality_engine(
    completed_customer_etl: dict[str, int | str],
) -> DataQualityEngine:
    """Create the reusable data-quality engine."""

    return DataQualityEngine()


@pytest.fixture(scope="module")
def data_quality_results(
    data_quality_engine: DataQualityEngine,
) -> list[dict[str, Any]]:
    """Execute all enabled rules once."""

    return data_quality_engine.run_all()


@pytest.mark.data_quality
@pytest.mark.database
@pytest.mark.regression
def test_data_quality_rules_loaded(
    data_quality_engine: DataQualityEngine,
) -> None:
    """Verify that enabled rules are loaded successfully."""

    assert data_quality_engine.rules, (
        "No enabled data-quality rules were loaded."
    )

    assert len(data_quality_engine.rules) == 23, (
        f"Expected 22 enabled rules, but loaded "
        f"{len(data_quality_engine.rules)}."
    )


@pytest.mark.data_quality
@pytest.mark.database
@pytest.mark.regression
def test_all_data_quality_rules_passed(
    data_quality_results: list[dict[str, Any]],
) -> None:
    """All configured data-quality rules must pass."""

    unsuccessful_results = [
        result
        for result in data_quality_results
        if result["status"] != "PASSED"
    ]

    failure_messages = [
        (
            f"{result['rule_id']}: "
            f"{result['status']} - "
            f"{result['message']}"
        )
        for result in unsuccessful_results
    ]

    assert not unsuccessful_results, (
        "\n".join(failure_messages)
    )


@pytest.mark.data_quality
@pytest.mark.oracle
@pytest.mark.database
def test_oracle_source_email_rule(
    data_quality_engine: DataQualityEngine,
) -> None:
    """Verify the intentional invalid source email threshold."""

    result = data_quality_engine.run_rule(
        "ORA_CUSTOMER_EMAIL_PATTERN"
    )

    assert result["status"] == "PASSED"
    assert result["actual_value"] == 1


@pytest.mark.data_quality
@pytest.mark.mysql
@pytest.mark.database
def test_mysql_golden_customer_count_rule(
    data_quality_engine: DataQualityEngine,
) -> None:
    """Verify the golden-customer row-count rule."""

    result = data_quality_engine.run_rule(
        "MYSQL_GOLDEN_ROW_COUNT"
    )

    assert result["status"] == "PASSED"
    assert result["actual_value"] == 3


@pytest.mark.data_quality
@pytest.mark.mysql
@pytest.mark.database
def test_mysql_customer_xref_count_rule(
    data_quality_engine: DataQualityEngine,
) -> None:
    """Verify the customer-XREF row-count rule."""

    result = data_quality_engine.run_rule(
        "MYSQL_XREF_ROW_COUNT"
    )

    assert result["status"] == "PASSED"
    assert result["actual_value"] == 4


@pytest.mark.data_quality
@pytest.mark.mysql
@pytest.mark.database
def test_mysql_rejected_record_count_rule(
    data_quality_engine: DataQualityEngine,
) -> None:
    """Verify the rejected-record count."""

    result = data_quality_engine.run_rule(
        "MYSQL_REJECTED_ROW_COUNT"
    )

    assert result["status"] == "PASSED"
    assert result["actual_value"] == 1


@pytest.mark.data_quality
@pytest.mark.mysql
@pytest.mark.database
def test_no_orphan_customer_xrefs_rule(
    data_quality_engine: DataQualityEngine,
) -> None:
    """Verify XREF referential integrity."""

    result = data_quality_engine.run_rule(
        "MYSQL_XREF_GOLDEN_REFERENCE"
    )

    assert result["status"] == "PASSED"
    assert result["actual_value"] == 0


@pytest.mark.data_quality
@pytest.mark.database
def test_data_quality_summary(
    data_quality_engine: DataQualityEngine,
    data_quality_results: list[dict[str, Any]],
) -> None:
    """Verify the overall execution summary."""

    summary = data_quality_engine.create_summary(
        data_quality_results
    )

    assert summary["total_rules"] == 23
    assert summary["passed_rules"] == 23
    assert summary["failed_rules"] == 0
    assert summary["error_rules"] == 0


@pytest.mark.data_quality
@pytest.mark.database
def test_data_quality_json_report(
    data_quality_engine: DataQualityEngine,
    data_quality_results: list[dict[str, Any]],
    tmp_path: Path,
) -> None:
    """Verify that the JSON report is generated correctly."""

    report_file = (
        tmp_path / "data_quality_report.json"
    )

    generated_file = data_quality_engine.save_report(
        results=data_quality_results,
        report_file=report_file,
    )

    assert generated_file.exists()

    report = json.loads(
        generated_file.read_text(encoding="utf-8")
    )

    assert report["total_rules"] == 23
    assert report["passed_rules"] == 23
    assert report["failed_rules"] == 0
    assert report["error_rules"] == 0
    assert len(report["results"]) == 23