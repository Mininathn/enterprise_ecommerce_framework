import json
from pathlib import Path
from typing import Any

from core.validation.data_quality_engine import DataQualityEngine
from utils.logger import get_logger


logger = get_logger(__name__)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "data_quality_report.json"
)


class DataQualityService:
    """Service layer for data-quality operations."""

    REPORT_PATH = REPORT_PATH

    @staticmethod
    def run_data_quality() -> dict[str, Any]:
        """
        Execute all enabled data-quality rules.

        The method also creates and saves the latest JSON report.
        """

        logger.info(
            "Executing Data Quality Engine through REST API."
        )

        engine = DataQualityEngine()

        results = engine.run_all()

        summary = engine.create_summary(
            results=results,
        )

        report_path = engine.save_report(
            results=results,
            report_file=DataQualityService.REPORT_PATH,
        )

        summary["report_path"] = str(report_path)

        logger.info(
            "Data Quality API execution completed. "
            "Total=%s, Passed=%s, Failed=%s, Errors=%s",
            summary["total_rules"],
            summary["passed_rules"],
            summary["failed_rules"],
            summary["error_rules"],
        )

        return summary

    @staticmethod
    def get_report() -> dict[str, Any] | None:
        """Return the latest generated data-quality report."""

        report_path = DataQualityService.REPORT_PATH

        if not report_path.exists():
            logger.warning(
                "Data-quality report was not found: %s",
                report_path,
            )

            return None

        with report_path.open(
            mode="r",
            encoding="utf-8",
        ) as file:
            report = json.load(file)

        logger.info(
            "Data-quality report retrieved successfully: %s",
            report_path,
        )

        return report

    @staticmethod
    def get_all_rules() -> list[dict[str, Any]]:
        """Return all enabled data-quality rules."""

        engine = DataQualityEngine()

        logger.info(
            "Retrieved %s enabled data-quality rules.",
            len(engine.rules),
        )

        return engine.rules

    @staticmethod
    def get_rule(
        rule_id: str,
    ) -> dict[str, Any] | None:
        """Return one configured data-quality rule by ID."""

        engine = DataQualityEngine()

        try:
            rule = engine.get_rule(
                rule_id=rule_id,
            )

            logger.info(
                "Data-quality rule retrieved: %s",
                rule_id,
            )

            return rule

        except KeyError:
            logger.warning(
                "Data-quality rule was not found: %s",
                rule_id,
            )

            return None