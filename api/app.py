from flask import Flask

from api.response import error_response
from api.routes.batch_routes import batch_blueprint
from api.routes.data_quality_routes import dq_blueprint
from api.routes.etl_routes import etl_blueprint
from api.routes.health_routes import health_blueprint
from utils.logger import get_logger


logger = get_logger(__name__)


def create_app(
    testing: bool = False,
) -> Flask:
    """Create and configure the Flask application."""

    app = Flask(__name__)

    app.config.update(
        TESTING=testing,
        JSON_SORT_KEYS=False,
    )

    app.register_blueprint(
        health_blueprint,
    )

    app.register_blueprint(
        etl_blueprint,
    )

    app.register_blueprint(
        batch_blueprint,
    )

    app.register_blueprint(
        dq_blueprint,
    )

    @app.errorhandler(404)
    def resource_not_found(error):
        return error_response(
            message="Requested API resource was not found",
            error=error,
            status_code=404,
        )

    @app.errorhandler(405)
    def method_not_allowed(error):
        return error_response(
            message="HTTP method is not allowed for this resource",
            error=error,
            status_code=405,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        logger.exception(
            "Unhandled API server error."
        )

        return error_response(
            message="Internal server error",
            error=error,
            status_code=500,
        )

    logger.info(
        "Enterprise Ecommerce API application created."
    )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )