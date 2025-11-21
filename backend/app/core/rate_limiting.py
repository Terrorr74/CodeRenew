"""
Rate limiting configuration for FastAPI application
Uses slowapi to prevent brute force attacks on authentication endpoints
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request


def get_client_identifier(request: Request) -> str:
    """
    Get client identifier for rate limiting
    Uses X-Forwarded-For header if behind a proxy, otherwise uses client IP

    Args:
        request: FastAPI Request object

    Returns:
        Client IP address or identifier
    """
    # Check for X-Forwarded-For header (when behind a reverse proxy like nginx)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For can contain multiple IPs, use the first one (original client)
        return forwarded.split(",")[0].strip()

    # Check for X-Real-IP header (alternative proxy header)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # Fall back to direct client IP
    return get_remote_address(request)


# Initialize rate limiter
# Storage backend: In-memory by default (can be changed to Redis in production)
# Key function: Uses client IP address for rate limiting
limiter = Limiter(
    key_func=get_client_identifier,
    default_limits=[],  # No default limits, we'll apply them per-endpoint
    headers_enabled=True,  # Include rate limit headers in responses
    storage_uri="memory://",  # Use in-memory storage (change to redis:// for production)
)


# Rate limit configurations for different endpoint types
# These can be adjusted based on security requirements

# Login endpoint: More permissive to allow legitimate login attempts
LOGIN_RATE_LIMIT = "5/15minutes"

# Registration endpoint: Stricter to prevent spam accounts
REGISTER_RATE_LIMIT = "3/hour"

# Password reset endpoints: Very strict to prevent abuse
PASSWORD_RESET_RATE_LIMIT = "3/hour"

# General API endpoints: Moderate limit
API_RATE_LIMIT = "60/minute"

# Public endpoints: More permissive
PUBLIC_RATE_LIMIT = "100/minute"
