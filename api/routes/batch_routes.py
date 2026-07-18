from flask import Blueprint, request

from api.response import error_response, success_response
from api.services.batch_service import BatchService
from utils.logger import get_logger


logger = get_logger(__name__)


batch_blueprint = Blueprint(
    "batch",
    __name__,
    url_prefix="/api/v1/batch",
)


@batch_blueprint.get("/latest")
def get_latest_batch():
    """Return the most recent ETL batch."""

    try:
        batch = BatchService.get_latest_batch()

        if batch is None:
            return error_response(
                message="No ETL batch was found",
                error="Batch-control table is empty",
                status_code=404,
            )

        return success_response(
            message="Latest ETL batch retrieved successfully",
            data=batch,
        )

    except Exception as error:
        logger.exception(
            "Failed to retrieve the latest ETL batch."
        )

        return error_response(
            message="Failed to retrieve the latest ETL batch",
            error=error,
            status_code=500,
        )


@batch_blueprint.get("/history")
def get_batch_history():
    """Return recent ETL batch history."""

    limit_value = request.args.get(
        "limit",
        default="10",
    )

    try:
        limit = int(limit_value)

    except ValueError:
        return error_response(
            message="Invalid query parameter",
            error="'limit' must be an integer",
            status_code=400,
        )

    if limit < 1 or limit > 100:
        return error_response(
            message="Invalid query parameter",
            error="'limit' must be between 1 and 100",
            status_code=400,
        )

    try:
        batches = BatchService.get_batch_history(
            limit=limit,
        )

        return success_response(
            message="ETL batch history retrieved successfully",
            data={
                "count": len(batches),
                "limit": limit,
                "batches": batches,
            },
        )

    except Exception as error:
        logger.exception(
            "Failed to retrieve ETL batch history."
        )

        return error_response(
            message="Failed to retrieve ETL batch history",
            error=error,
            status_code=500,
        )


@batch_blueprint.get("/<int:batch_id>")
def get_batch_by_id(
    batch_id: int,
):
    """Return one ETL batch by its ID."""

    try:
        batch = BatchService.get_batch_by_id(
            batch_id=batch_id,
        )

        if batch is None:
            return error_response(
                message="ETL batch was not found",
                error=f"Batch ID {batch_id} does not exist",
                status_code=404,
            )

        return success_response(
            message="ETL batch retrieved successfully",
            data=batch,
        )

    except Exception as error:
        logger.exception(
            "Failed to retrieve ETL batch ID %s.",
            batch_id,
        )

        return error_response(
            message="Failed to retrieve ETL batch",
            error=error,
            status_code=500,
        )