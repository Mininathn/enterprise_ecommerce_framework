from typing import Any

from core.etl.customer_etl import CustomerETL
from utils.logger import get_logger


logger = get_logger(__name__)


class ETLService:
    """Service layer for executing the customer ETL pipeline."""

    @staticmethod
    def run_customer_etl(
        reset_target: bool = True,
    ) -> dict[str, Any]:
        """
        Execute the Oracle-to-MySQL customer ETL process.

        Args:
            reset_target:
                When True, existing target customer records are cleared
                before loading fresh data.

        Returns:
            ETL execution summary.
        """

        logger.info(
            "REST API requested customer ETL execution. "
            "reset_target=%s",
            reset_target,
        )

        etl = CustomerETL()

        result = etl.run(
            reset_target=reset_target,
        )

        logger.info(
            "REST API customer ETL execution completed: %s",
            result,
        )

        return result