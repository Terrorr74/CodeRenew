"""
Security headers middleware
Adds security-related HTTP headers to all responses for defense in depth
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all HTTP responses

    Headers added:
    - Strict-Transport-Security (HSTS): Forces HTTPS connections
    - Content-Security-Policy (CSP): Prevents XSS attacks
    - X-Frame-Options: Prevents clickjacking
    - X-Content-Type-Options: Prevents MIME sniffing
    - X-XSS-Protection: Legacy XSS protection
    - Referrer-Policy: Controls referrer information
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add security headers to response"""
        response = await call_next(request)

        # HSTS: Force HTTPS for 1 year including subdomains
        # Note: Only enable in production with valid SSL certificate
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # CSP: Restrict resource loading to prevent XSS
        # Adjust this policy based on your frontend needs
        # Current policy allows same-origin + specific domains
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://api.stripe.com; "
            "frame-ancestors 'none';"
        )

        # Prevent page from being displayed in iframe (clickjacking protection)
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enable XSS filter in older browsers (legacy but doesn't hurt)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Control referrer information sent with requests
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Prevent DNS prefetching to protect user privacy
        response.headers["X-DNS-Prefetch-Control"] = "off"

        # Prevent browser from caching sensitive data
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        return response
