"""
Input sanitization utilities
Provides validation and sanitization for user inputs to prevent XSS and injection attacks
"""
import re
import html
from typing import Any


def sanitize_html(value: str) -> str:
    """
    Sanitize HTML/script tags from input to prevent XSS attacks

    Args:
        value: Input string to sanitize

    Returns:
        Sanitized string with HTML entities escaped
    """
    if not isinstance(value, str):
        return value

    # Escape HTML entities
    sanitized = html.escape(value)

    # Remove any script tags that might have slipped through
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)

    # Remove any event handlers (onclick, onerror, etc.)
    sanitized = re.sub(r'\s*on\w+\s*=', '', sanitized, flags=re.IGNORECASE)

    return sanitized


def sanitize_sql_like_pattern(value: str) -> str:
    """
    Sanitize SQL LIKE pattern special characters
    Note: SQLAlchemy already prevents SQL injection through parameterized queries
    This is an additional safety layer for LIKE queries

    Args:
        value: Input string

    Returns:
        String with SQL special characters escaped
    """
    if not isinstance(value, str):
        return value

    # Escape SQL LIKE special characters
    value = value.replace('\\', '\\\\')
    value = value.replace('%', '\\%')
    value = value.replace('_', '\\_')

    return value


def validate_email_format(email: str) -> str:
    """
    Validate email format (basic check)
    Pydantic's EmailStr already does this, but this provides additional validation

    Args:
        email: Email address to validate

    Returns:
        Lowercase email if valid

    Raises:
        ValueError: If email format is invalid
    """
    if not email or not isinstance(email, str):
        raise ValueError("Email must be a non-empty string")

    # Basic email regex (RFC 5322 simplified)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")

    # Normalize to lowercase
    return email.lower().strip()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal attacks

    Args:
        filename: Original filename

    Returns:
        Sanitized filename

    Raises:
        ValueError: If filename is invalid
    """
    if not filename or not isinstance(filename, str):
        raise ValueError("Filename must be a non-empty string")

    # Remove directory traversal attempts
    filename = filename.replace('../', '').replace('..\\', '')

    # Remove path separators
    filename = filename.replace('/', '_').replace('\\', '_')

    # Remove null bytes
    filename = filename.replace('\x00', '')

    # Allow only alphanumeric, dash, underscore, and dot
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

    # Prevent hidden files
    if filename.startswith('.'):
        filename = '_' + filename

    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')

    return filename


def validate_url(url: str) -> str:
    """
    Validate URL format and scheme

    Args:
        url: URL to validate

    Returns:
        The URL if valid

    Raises:
        ValueError: If URL is invalid or uses dangerous scheme
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")

    # Allow only http/https schemes
    if not url.startswith(('http://', 'https://')):
        raise ValueError("URL must start with http:// or https://")

    # Basic URL validation
    url_pattern = r'^https?://[a-zA-Z0-9.-]+(?:\:[0-9]+)?(?:/[^s]*)?$'
    if not re.match(url_pattern, url):
        raise ValueError("Invalid URL format")

    return url.strip()


def truncate_string(value: str, max_length: int = 1000) -> str:
    """
    Truncate string to maximum length to prevent DoS via large inputs

    Args:
        value: String to truncate
        max_length: Maximum allowed length

    Returns:
        Truncated string
    """
    if not isinstance(value, str):
        return value

    if len(value) > max_length:
        return value[:max_length]

    return value
