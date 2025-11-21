"""
Unit tests for security utilities
Tests JWT token handling and password hashing
"""
import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    pwd_context
)


class TestPasswordHashing:
    """Test password hashing functionality"""

    def test_get_password_hash_generates_hash(self):
        """Test that password hashing generates a hash"""
        # Arrange
        password = "TestPassword123!"

        # Act
        hashed = get_password_hash(password)

        # Assert
        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password  # Hash should not be plain password
        assert len(hashed) > 20  # Bcrypt hashes are long

    def test_get_password_hash_different_for_same_password(self):
        """Test that same password generates different hashes (salt)"""
        # Arrange
        password = "TestPassword123!"

        # Act
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Assert
        assert hash1 != hash2  # Different salts

    def test_get_password_hash_uses_bcrypt(self):
        """Test that bcrypt is used for hashing"""
        # Arrange
        password = "TestPassword123!"

        # Act
        hashed = get_password_hash(password)

        # Assert
        # Bcrypt hashes start with $2b$ or $2a$ or $2y$
        assert hashed.startswith("$2") or hashed.startswith("$2a") or hashed.startswith("$2b")

    def test_verify_password_correct_password(self):
        """Test that correct password verification succeeds"""
        # Arrange
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        # Act
        result = verify_password(password, hashed)

        # Assert
        assert result is True

    def test_verify_password_incorrect_password(self):
        """Test that incorrect password verification fails"""
        # Arrange
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = get_password_hash(password)

        # Act
        result = verify_password(wrong_password, hashed)

        # Assert
        assert result is False

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive"""
        # Arrange
        password = "TestPassword123!"
        wrong_case = "testpassword123!"
        hashed = get_password_hash(password)

        # Act
        result = verify_password(wrong_case, hashed)

        # Assert
        assert result is False

    def test_verify_password_empty_password(self):
        """Test verification with empty password"""
        # Arrange
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        # Act
        result = verify_password("", hashed)

        # Assert
        assert result is False

    def test_password_context_configured(self):
        """Test that password context is properly configured"""
        # Assert
        assert pwd_context is not None
        assert "bcrypt" in pwd_context.schemes()


class TestJWTTokenCreation:
    """Test JWT access token creation"""

    def test_create_access_token_generates_token(self):
        """Test that access token is generated"""
        # Arrange
        data = {"sub": "test@example.com"}

        # Act
        token = create_access_token(data)

        # Assert
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20  # JWT tokens are long

    def test_create_access_token_has_three_parts(self):
        """Test that JWT token has three parts (header.payload.signature)"""
        # Arrange
        data = {"sub": "test@example.com"}

        # Act
        token = create_access_token(data)

        # Assert
        parts = token.split(".")
        assert len(parts) == 3  # Header, payload, signature

    def test_create_access_token_includes_subject(self):
        """Test that token includes the subject claim"""
        # Arrange
        email = "test@example.com"
        data = {"sub": email}

        # Act
        token = create_access_token(data)
        decoded = decode_access_token(token)

        # Assert
        assert decoded is not None
        assert decoded["sub"] == email

    def test_create_access_token_includes_expiration(self):
        """Test that token includes expiration claim"""
        # Arrange
        data = {"sub": "test@example.com"}

        # Act
        token = create_access_token(data)
        decoded = decode_access_token(token)

        # Assert
        assert decoded is not None
        assert "exp" in decoded
        assert isinstance(decoded["exp"], (int, float))

    def test_create_access_token_default_expiration(self):
        """Test that default expiration is applied"""
        # Arrange
        data = {"sub": "test@example.com"}

        # Act
        with freeze_time("2024-01-01 12:00:00"):
            token = create_access_token(data)
            decoded = decode_access_token(token)

        # Assert
        assert decoded is not None
        exp_timestamp = decoded["exp"]
        exp_datetime = datetime.utcfromtimestamp(exp_timestamp)

        # Should expire in the future (default is typically 15-60 minutes)
        now = datetime.strptime("2024-01-01 12:00:00", "%Y-%m-%d %H:%M:%S")
        assert exp_datetime > now

    def test_create_access_token_custom_expiration(self):
        """Test that custom expiration can be set"""
        # Arrange
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(hours=2)

        # Act
        with freeze_time("2024-01-01 12:00:00"):
            token = create_access_token(data, expires_delta=expires_delta)
            decoded = decode_access_token(token)

        # Assert
        assert decoded is not None
        exp_timestamp = decoded["exp"]
        exp_datetime = datetime.utcfromtimestamp(exp_timestamp)

        expected_exp = datetime.strptime("2024-01-01 14:00:00", "%Y-%m-%d %H:%M:%S")
        # Allow 1 second tolerance
        assert abs((exp_datetime - expected_exp).total_seconds()) < 1

    def test_create_access_token_preserves_additional_claims(self):
        """Test that additional claims are preserved in token"""
        # Arrange
        data = {
            "sub": "test@example.com",
            "role": "admin",
            "user_id": 123
        }

        # Act
        token = create_access_token(data)
        decoded = decode_access_token(token)

        # Assert
        assert decoded is not None
        assert decoded["sub"] == "test@example.com"
        assert decoded["role"] == "admin"
        assert decoded["user_id"] == 123

    def test_create_access_token_different_for_same_data(self):
        """Test that tokens are different even with same data (due to expiration)"""
        # Arrange
        data = {"sub": "test@example.com"}

        # Act
        token1 = create_access_token(data)
        token2 = create_access_token(data)

        # Assert
        assert token1 != token2  # Different exp times


class TestJWTTokenDecoding:
    """Test JWT access token decoding"""

    def test_decode_access_token_valid_token(self):
        """Test decoding a valid token"""
        # Arrange
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        # Act
        decoded = decode_access_token(token)

        # Assert
        assert decoded is not None
        assert decoded["sub"] == "test@example.com"

    def test_decode_access_token_expired_token(self):
        """Test that expired token returns None"""
        # Arrange
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(data, expires_delta=expires_delta)

        # Act
        decoded = decode_access_token(token)

        # Assert
        assert decoded is None

    def test_decode_access_token_invalid_token(self):
        """Test that invalid token returns None"""
        # Arrange
        invalid_token = "not.a.valid.jwt.token"

        # Act
        decoded = decode_access_token(invalid_token)

        # Assert
        assert decoded is None

    def test_decode_access_token_tampered_token(self):
        """Test that tampered token returns None"""
        # Arrange
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        # Tamper with the token
        parts = token.split(".")
        tampered_token = parts[0] + ".tampered." + parts[2]

        # Act
        decoded = decode_access_token(tampered_token)

        # Assert
        assert decoded is None

    def test_decode_access_token_empty_token(self):
        """Test decoding empty token"""
        # Act
        decoded = decode_access_token("")

        # Assert
        assert decoded is None

    def test_decode_access_token_malformed_token(self):
        """Test decoding malformed token"""
        # Arrange
        malformed_tokens = [
            "single_part",
            "only.two.parts",
            ".....",
            None
        ]

        # Act & Assert
        for token in malformed_tokens:
            if token is not None:
                decoded = decode_access_token(token)
                assert decoded is None

    def test_decode_access_token_preserves_all_claims(self):
        """Test that all claims are preserved in decoding"""
        # Arrange
        data = {
            "sub": "test@example.com",
            "role": "user",
            "permissions": ["read", "write"],
            "user_id": 42
        }
        token = create_access_token(data)

        # Act
        decoded = decode_access_token(token)

        # Assert
        assert decoded is not None
        assert decoded["sub"] == "test@example.com"
        assert decoded["role"] == "user"
        assert decoded["permissions"] == ["read", "write"]
        assert decoded["user_id"] == 42


class TestJWTTokenLifecycle:
    """Test JWT token lifecycle"""

    def test_token_valid_before_expiration(self):
        """Test that token is valid before expiration"""
        # Arrange
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(hours=1)

        # Act
        with freeze_time("2024-01-01 12:00:00"):
            token = create_access_token(data, expires_delta=expires_delta)

        # Still within expiration time
        with freeze_time("2024-01-01 12:30:00"):
            decoded = decode_access_token(token)

        # Assert
        assert decoded is not None
        assert decoded["sub"] == "test@example.com"

    def test_token_invalid_after_expiration(self):
        """Test that token is invalid after expiration"""
        # Arrange
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(hours=1)

        # Act
        with freeze_time("2024-01-01 12:00:00"):
            token = create_access_token(data, expires_delta=expires_delta)

        # After expiration time
        with freeze_time("2024-01-01 13:01:00"):
            decoded = decode_access_token(token)

        # Assert
        assert decoded is None

    def test_token_valid_at_creation_time(self):
        """Test that token is immediately valid after creation"""
        # Arrange
        data = {"sub": "test@example.com"}

        # Act
        token = create_access_token(data)
        decoded = decode_access_token(token)

        # Assert
        assert decoded is not None


@pytest.mark.security
class TestSecurityBestPractices:
    """Test security best practices in implementation"""

    def test_password_hash_uses_strong_algorithm(self):
        """Test that bcrypt (strong algorithm) is used"""
        # Arrange
        password = "TestPassword123!"

        # Act
        hashed = get_password_hash(password)

        # Assert
        # Bcrypt hashes have cost factor embedded
        assert hashed.startswith("$2")  # Bcrypt identifier

    def test_password_hash_has_sufficient_work_factor(self):
        """Test that password hashing uses sufficient work factor"""
        # Arrange
        password = "TestPassword123!"

        # Act
        hashed = get_password_hash(password)

        # Assert
        # Bcrypt format: $2b$<cost>$...
        # Cost should be at least 10 for security
        parts = hashed.split("$")
        if len(parts) >= 3:
            cost = int(parts[2])
            assert cost >= 10, f"Bcrypt cost factor {cost} is too low (should be >= 10)"

    def test_jwt_tokens_are_not_predictable(self):
        """Test that JWT tokens are not predictable"""
        # Arrange
        data = {"sub": "test@example.com"}

        # Act
        tokens = [create_access_token(data) for _ in range(5)]

        # Assert
        # All tokens should be unique
        assert len(set(tokens)) == len(tokens)

    def test_jwt_includes_signature(self):
        """Test that JWT tokens include cryptographic signature"""
        # Arrange
        data = {"sub": "test@example.com"}

        # Act
        token = create_access_token(data)
        parts = token.split(".")

        # Assert
        assert len(parts) == 3
        # Signature part should not be empty
        assert len(parts[2]) > 0

    def test_password_verification_timing_safe(self):
        """Test that password verification uses constant-time comparison"""
        # This is more of a documentation test - bcrypt is timing-safe by design
        # Arrange
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        # Act & Assert
        # Both should take similar time (bcrypt handles this internally)
        result1 = verify_password(password, hashed)
        result2 = verify_password("WrongPassword!", hashed)

        assert result1 is True
        assert result2 is False


@pytest.mark.parametrize("password", [
    "SimplePass123!",
    "C0mpl3x$P@ssw0rd",
    "MySecur3P@ss!",
    "Test1234!@#$",
])
def test_password_hash_and_verify_parametrized(password):
    """Parametrized test for password hashing and verification"""
    # Arrange & Act
    hashed = get_password_hash(password)

    # Assert
    assert verify_password(password, hashed) is True
    assert verify_password(password + "wrong", hashed) is False
