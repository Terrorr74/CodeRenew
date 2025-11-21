"""
Error handling middleware for CodeRenew API
Provides standardized error responses across the application
"""
import logging
import traceback
from typing import Callable
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError as PydanticValidationError
import pybreaker

from app.core.exceptions import CodeRenewException, CircuitBreakerOpenError
from app.core.config import settings

logger = logging.getLogger(__name__)


def create_error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: dict = None,
    request_id: str = None
) -> JSONResponse:
    """Create standardized error response"""
    content = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
        }
    }

    if details:
        content["error"]["details"] = details

    if request_id:
        content["error"]["request_id"] = request_id

    return JSONResponse(status_code=status_code, content=content)


async def coderenew_exception_handler(request: Request, exc: CodeRenewException) -> JSONResponse:
    """Handle CodeRenew custom exceptions"""
    request_id = getattr(request.state, "request_id", None)

    logger.warning(
        f"CodeRenew exception: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "request_id": request_id,
            "path": request.url.path
        }
    )

    return create_error_response(
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        request_id=request_id
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette HTTP exceptions"""
    request_id = getattr(request.state, "request_id", None)

    error_codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
        504: "GATEWAY_TIMEOUT"
    }

    error_code = error_codes.get(exc.status_code, "HTTP_ERROR")

    return create_error_response(
        status_code=exc.status_code,
        error_code=error_code,
        message=str(exc.detail),
        request_id=request_id
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors"""
    request_id = getattr(request.state, "request_id", None)

    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        details={"errors": errors},
        request_id=request_id
    )


async def circuit_breaker_exception_handler(request: Request, exc: pybreaker.CircuitBreakerError) -> JSONResponse:
    """Handle circuit breaker open errors"""
    request_id = getattr(request.state, "request_id", None)

    logger.error(
        f"Circuit breaker open: {str(exc)}",
        extra={"request_id": request_id, "path": request.url.path}
    )

    return create_error_response(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        error_code="CIRCUIT_BREAKER_OPEN",
        message="Service temporarily unavailable due to repeated failures. Please try again later.",
        details={"retry_after": 30},
        request_id=request_id
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    request_id = getattr(request.state, "request_id", None)

    # Log full traceback for debugging
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "traceback": traceback.format_exc()
        }
    )

    # Return generic error in production, detailed in debug mode
    if settings.DEBUG:
        message = f"{type(exc).__name__}: {str(exc)}"
        details = {"traceback": traceback.format_exc().split("\n")}
    else:
        message = "An unexpected error occurred"
        details = None

    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_ERROR",
        message=message,
        details=details,
        request_id=request_id
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app"""
    app.add_exception_handler(CodeRenewException, coderenew_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(pybreaker.CircuitBreakerError, circuit_breaker_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
