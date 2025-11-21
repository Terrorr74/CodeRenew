"""
Custom exceptions for CodeRenew API
Standardized error handling with proper HTTP status codes and error codes
"""
from typing import Optional, Dict, Any


class CodeRenewException(Exception):
    """Base exception for all CodeRenew errors"""

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# Authentication Errors (401, 403)
class AuthenticationError(CodeRenewException):
    """Authentication failed"""
    def __init__(self, message: str = "Authentication required", details: Optional[Dict] = None):
        super().__init__(message, "AUTH_REQUIRED", 401, details)


class InvalidCredentialsError(CodeRenewException):
    """Invalid credentials provided"""
    def __init__(self, message: str = "Invalid credentials", details: Optional[Dict] = None):
        super().__init__(message, "INVALID_CREDENTIALS", 401, details)


class TokenExpiredError(CodeRenewException):
    """JWT token has expired"""
    def __init__(self, message: str = "Token has expired", details: Optional[Dict] = None):
        super().__init__(message, "TOKEN_EXPIRED", 401, details)


class InsufficientPermissionsError(CodeRenewException):
    """User lacks required permissions"""
    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict] = None):
        super().__init__(message, "INSUFFICIENT_PERMISSIONS", 403, details)


# Resource Errors (404, 409)
class ResourceNotFoundError(CodeRenewException):
    """Requested resource not found"""
    def __init__(self, resource: str = "Resource", resource_id: Optional[str] = None):
        details = {"resource": resource}
        if resource_id:
            details["resource_id"] = resource_id
        message = f"{resource} not found"
        super().__init__(message, "RESOURCE_NOT_FOUND", 404, details)


class ResourceConflictError(CodeRenewException):
    """Resource conflict (e.g., duplicate)"""
    def __init__(self, message: str = "Resource already exists", details: Optional[Dict] = None):
        super().__init__(message, "RESOURCE_CONFLICT", 409, details)


# Validation Errors (400, 422)
class ValidationError(CodeRenewException):
    """Input validation failed"""
    def __init__(self, message: str = "Validation failed", details: Optional[Dict] = None):
        super().__init__(message, "VALIDATION_ERROR", 422, details)


class BadRequestError(CodeRenewException):
    """Bad request format"""
    def __init__(self, message: str = "Bad request", details: Optional[Dict] = None):
        super().__init__(message, "BAD_REQUEST", 400, details)


# External Service Errors (502, 503, 504)
class ExternalServiceError(CodeRenewException):
    """External service failed"""
    def __init__(self, service: str, message: str = "External service error", details: Optional[Dict] = None):
        details = details or {}
        details["service"] = service
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", 502, details)


class ClaudeAPIError(ExternalServiceError):
    """Claude API specific error"""
    def __init__(self, message: str = "Claude API error", details: Optional[Dict] = None):
        super().__init__("claude_api", message, details)
        self.error_code = "CLAUDE_API_ERROR"


class WordPressAPIError(ExternalServiceError):
    """WordPress API specific error"""
    def __init__(self, message: str = "WordPress API error", details: Optional[Dict] = None):
        super().__init__("wordpress_api", message, details)
        self.error_code = "WORDPRESS_API_ERROR"


class ServiceUnavailableError(CodeRenewException):
    """Service temporarily unavailable"""
    def __init__(self, message: str = "Service temporarily unavailable", retry_after: Optional[int] = None):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(message, "SERVICE_UNAVAILABLE", 503, details)


class CircuitBreakerOpenError(CodeRenewException):
    """Circuit breaker is open"""
    def __init__(self, service: str, retry_after: Optional[int] = 30):
        message = f"Service {service} is temporarily unavailable due to repeated failures"
        details = {"service": service, "retry_after": retry_after}
        super().__init__(message, "CIRCUIT_BREAKER_OPEN", 503, details)


class TimeoutError(CodeRenewException):
    """Request timeout"""
    def __init__(self, message: str = "Request timed out", details: Optional[Dict] = None):
        super().__init__(message, "TIMEOUT", 504, details)


# Rate Limiting (429)
class RateLimitExceededError(CodeRenewException):
    """Rate limit exceeded"""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(message, "RATE_LIMIT_EXCEEDED", 429, details)


# Business Logic Errors
class QuotaExceededError(CodeRenewException):
    """User quota exceeded"""
    def __init__(self, message: str = "Quota exceeded", details: Optional[Dict] = None):
        super().__init__(message, "QUOTA_EXCEEDED", 402, details)


class ScanError(CodeRenewException):
    """Scan operation failed"""
    def __init__(self, message: str = "Scan failed", details: Optional[Dict] = None):
        super().__init__(message, "SCAN_ERROR", 500, details)
