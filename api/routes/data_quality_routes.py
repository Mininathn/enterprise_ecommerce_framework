from flask import Blueprint

from api.response import error_response, success_response
from api.services.data_quality_service import DataQualityService
from utils.logger import get_logger


logger = get_logger(__name__)


dq_blueprint = Blueprint(
    "data_quality",
    __name__,
    url_prefix="/api/v1/data-quality",
)


@dq_blueprint.get("/run")
def run_data_quality():
    """Execute all configured data-quality rules."""

    try:
        summary = DataQualityService.run_data_quality()

        return success_response(
            message="Data Quality executed successfully",
            data=summary,
        )

    except Exception as error:
        logger.exception(
            "Data Quality API execution failed."
        )

        return error_response(
            message="Data Quality execution failed",
            error=error,
            status_code=500,
        )


@dq_blueprint.get("/report")
def get_report():
    """Return the latest generated data-quality report."""

    try:
        report = DataQualityService.get_report()

        if report is None:
            return error_response(
                message="Report not found",
                error="Run data quality first.",
                status_code=404,
            )

        return success_response(
            message="Latest report retrieved successfully",
            data=report,
        )

    except Exception as error:
        logger.exception(
            "Failed to retrieve the data-quality report."
        )

        return error_response(
            message="Failed to retrieve the report",
            error=error,
            status_code=500,
        )


@dq_blueprint.get("/rules")
def get_rules():
    """Return all enabled data-quality rules."""

    try:
        rules = DataQualityService.get_all_rules()

        return success_response(
            message="Rules retrieved successfully",
            data={
                "count": len(rules),
                "rules": rules,
            },
        )

    except Exception as error:
        logger.exception(
            "Failed to retrieve data-quality rules."
        )

        return error_response(
            message="Failed to retrieve rules",
            error=error,
            status_code=500,
        )


@dq_blueprint.get("/rule/<string:rule_id>")
def get_rule(rule_id: str):
    """Return one configured data-quality rule."""

    try:
        rule = DataQualityService.get_rule(rule_id)

        if rule is None:
            return error_response(
                message="Rule not found",
                error=f"Rule ID '{rule_id}' does not exist",
                status_code=404,
            )

        return success_response(
            message="Rule retrieved successfully",
            data=rule,
        )

    except Exception as error:
        logger.exception(
            "Failed to retrieve data-quality rule %s.",
            rule_id,
        )

        return error_response(
            message="Failed to retrieve rule",
            error=error,
            status_code=500,
        )