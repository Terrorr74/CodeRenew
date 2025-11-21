"""
Password policy validation
Enforces strong password requirements to prevent weak credentials
"""
import re
from typing import Set

# Common weak passwords (top 100 most commonly used passwords)
# In production, consider loading from a larger file or using a library like 'pwned-passwords'
COMMON_PASSWORDS: Set[str] = {
    "password", "123456", "123456789", "12345678", "12345", "1234567", "password1",
    "qwerty", "abc123", "111111", "123123", "admin", "letmein", "welcome", "monkey",
    "1234567890", "password123", "qwerty123", "000000", "1234", "dragon", "master",
    "sunshine", "princess", "football", "shadow", "iloveyou", "superman", "michael",
    "jesus", "ninja", "mustang", "121212", "batman", "passw0rd", "trustno1", "starwars",
    "charlie", "654321", "ashley", "bailey", "access", "love", "whatever", "jordan",
    "hunter", "aa123456", "lovely", "hello", "password!", "password1!", "Password1",
    "Password123", "qwertyuiop", "test", "admin123", "root", "welcome123",
}


class PasswordValidationError(ValueError):
    """Custom exception for password validation errors"""
    pass


def validate_password_strength(password: str) -> str:
    """
    Validate password meets security requirements

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    - Not in common password list

    Args:
        password: The password to validate

    Returns:
        The password if valid

    Raises:
        PasswordValidationError: If password doesn't meet requirements
    """
    if not password or len(password) < 8:
        raise PasswordValidationError(
            "Password must be at least 8 characters long"
        )

    if len(password) > 128:
        raise PasswordValidationError(
            "Password must not exceed 128 characters"
        )

    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        raise PasswordValidationError(
            "Password must contain at least one uppercase letter"
        )

    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        raise PasswordValidationError(
            "Password must contain at least one lowercase letter"
        )

    # Check for digit
    if not re.search(r'\d', password):
        raise PasswordValidationError(
            "Password must contain at least one number"
        )

    # Check for special character
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        raise PasswordValidationError(
            "Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)"
        )

    # Check against common passwords (case-insensitive)
    if password.lower() in COMMON_PASSWORDS:
        raise PasswordValidationError(
            "This password is too common. Please choose a more unique password"
        )

    # Check for common patterns
    if password.lower() in ['password', 'admin', 'user', 'root', 'test']:
        raise PasswordValidationError(
            "Password contains common words. Please choose a more unique password"
        )

    # Check for sequential characters (123, abc, etc.)
    if re.search(r'(012|123|234|345|456|567|678|789|abc|bcd|cde|def|efg|fgh)', password.lower()):
        raise PasswordValidationError(
            "Password should not contain sequential characters"
        )

    return password


def get_password_strength_score(password: str) -> int:
    """
    Calculate password strength score (0-100)

    Args:
        password: The password to score

    Returns:
        Score from 0 to 100
    """
    score = 0

    # Length scoring
    if len(password) >= 8:
        score += 20
    if len(password) >= 12:
        score += 10
    if len(password) >= 16:
        score += 10

    # Character variety
    if re.search(r'[a-z]', password):
        score += 10
    if re.search(r'[A-Z]', password):
        score += 10
    if re.search(r'\d', password):
        score += 10
    if re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        score += 15

    # Complexity bonuses
    unique_chars = len(set(password))
    if unique_chars >= 8:
        score += 10
    if unique_chars >= 12:
        score += 5

    # Penalty for common patterns
    if password.lower() in COMMON_PASSWORDS:
        score -= 50
    if re.search(r'(012|123|234|345|456|567|678|789)', password):
        score -= 10

    return max(0, min(100, score))
