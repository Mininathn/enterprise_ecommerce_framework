from datetime import datetime, timezone
from typing import Any


def success_response(
    message: str,
    data: Any = None,
    status_code: int = 200,
) -> tuple[dict[str, Any], int]:
    """Create a consistent successful API response."""

    response = {
        "status": "SUCCESS",
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }

    return response, status_code


def error_response(
    message: str,
    error: Any = None,
    status_code: int = 500,
) -> tuple[dict[str, Any], int]:
    """Create a consistent error API response."""

    response = {
        "status": "ERROR",
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error": str(error) if error is not None else None,
    }

    return response, status_code