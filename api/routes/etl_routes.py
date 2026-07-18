from flask import Blueprint, request

from api.response import error_response, success_response
from api.services.etl_service import ETLService
from utils.logger import get_logger


logger = get_logger(__name__)


etl_blueprint = Blueprint(
    "etl",
    __name__,
    url_prefix="/api/v1/etl",
)


@etl_blueprint.post("/run")
def run_customer_etl():
    """
    Trigger the Oracle-to-MySQL customer ETL process.

    Optional JSON body:

    {
        "reset_target": true
    }
    """

    request_body = request.get_json(
        silent=True,
    ) or {}

    reset_target = request_body.get(
        "reset_target",
        True,
    )

    if not isinstance(reset_target, bool):
        return error_response(
            message="Invalid request body",
            error="'reset_target' must be true or false",
            status_code=400,
        )

    try:
        result = ETLService.run_customer_etl(
            reset_target=reset_target,
        )

        return success_response(
            message="Customer ETL completed successfully",
            data=result,
            status_code=200,
        )

    except Exception as error:
        logger.exception(
            "Customer ETL API execution failed."
        )

        return error_response(
            message="Customer ETL execution failed",
            error=error,
            status_code=500,
        )