"""Application exception types and FastAPI handlers."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.utils.logger import get_logger
from app.utils.metrics import runtime_metrics

logger = get_logger(__name__)


class AIRAError(Exception):
    """Base exception for expected AIRA application errors."""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ResourceNotFoundError(AIRAError):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str = "Resource not found.") -> None:
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ValidationFailedError(AIRAError):
    """Raised when domain validation fails."""

    def __init__(self, message: str = "Validation failed.") -> None:
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


async def aira_error_handler(request: Request, exc: AIRAError) -> JSONResponse:
    """Return structured JSON for expected AIRA errors."""
    runtime_metrics.increment_error()
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.message, "path": request.url.path},
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Return structured JSON for FastAPI HTTP exceptions."""
    if exc.status_code >= 400:
        runtime_metrics.increment_error()
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail, "path": request.url.path},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Return structured JSON for request validation errors."""
    runtime_metrics.increment_error()
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "error": "Request validation failed.", "details": exc.errors(), "path": request.url.path},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return structured JSON for unexpected errors and log them."""
    runtime_metrics.increment_error()
    logger.exception("Unhandled exception on %s", request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "error": "Internal server error.", "path": request.url.path},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register application exception handlers."""
    app.add_exception_handler(AIRAError, aira_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
