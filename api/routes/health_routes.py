from flask import Blueprint

from api.response import success_response


health_blueprint = Blueprint(
    "health",
    __name__,
)


@health_blueprint.get("/health")
def health_check():
    """Confirm that the Flask service is running."""

    return success_response(
        message="API is healthy",
        data={
            "service": "enterprise-ecommerce-api",
            "state": "UP",
        },
    )


@health_blueprint.get("/ready")
def readiness_check():
    """Confirm that the API application is ready."""

    return success_response(
        message="API is ready to receive requests",
        data={
            "ready": True,
        },
    )


@health_blueprint.get("/api/version")
def api_version():
    """Return framework and API version information."""

    return success_response(
        message="Version information retrieved successfully",
        data={
            "framework": (
                "Enterprise Ecommerce ETL Automation Framework"
            ),
            "api_version": "v1",
            "framework_version": "1.0.0",
            "environment": "local",
        },
    )