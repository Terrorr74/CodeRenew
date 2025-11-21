"""
Unit tests for authentication API endpoints
Tests registration, login, and authentication flow
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status


class TestRegistrationEndpoint:
    """Test user registration endpoint"""

    def test_register_new_user_success(self, client, db_session):
        """Test successful user registration"""
        # Arrange
        user_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "name": "New User",
            "company": "Test Company"
        }

        # Act
        response = client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["name"] == user_data["name"]
        assert "password" not in data["user"]  # Password should not be returned
        assert "hashed_password" not in data["user"]

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email"""
        # Arrange
        user_data = {
            "email": test_user.email,
            "password": "SecurePass123!",
            "name": "Duplicate User"
        }

        # Act
        response = client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email_format(self, client):
        """Test registration with invalid email format"""
        # Arrange
        user_data = {
            "email": "not-an-email",
            "password": "SecurePass123!",
            "name": "Test User"
        }

        # Act
        response = client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_weak_password(self, client):
        """Test registration with weak password"""
        # Arrange
        user_data = {
            "email": "newuser@example.com",
            "password": "weak",  # Too weak
            "name": "Test User"
        }

        # Act
        response = client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_missing_required_fields(self, client):
        """Test registration with missing required fields"""
        # Arrange
        incomplete_data = {
            "email": "test@example.com"
            # Missing password and name
        }

        # Act
        response = client.post("/api/v1/auth/register", json=incomplete_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_optional_company_field(self, client):
        """Test that company field is optional"""
        # Arrange
        user_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "name": "Test User"
            # No company field
        }

        # Act
        response = client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["user"]["company"] is None or data["user"]["company"] == ""

    def test_register_auto_login(self, client):
        """Test that registration returns a valid token for auto-login"""
        # Arrange
        user_data = {
            "email": "autouser@example.com",
            "password": "SecurePass123!",
            "name": "Auto User"
        }

        # Act
        response = client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        token = response.json()["access_token"]

        # Verify token works for authenticated endpoints
        headers = {"Authorization": f"Bearer {token}"}
        me_response = client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == status.HTTP_200_OK

    def test_register_new_user_unverified(self, client):
        """Test that new users start as unverified"""
        # Arrange
        user_data = {
            "email": "unverified@example.com",
            "password": "SecurePass123!",
            "name": "Unverified User"
        }

        # Act
        response = client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        user = response.json()["user"]
        assert user["is_verified"] is False

    def test_register_new_user_onboarding_incomplete(self, client):
        """Test that new users have incomplete onboarding"""
        # Arrange
        user_data = {
            "email": "onboarding@example.com",
            "password": "SecurePass123!",
            "name": "Onboarding User"
        }

        # Act
        response = client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        user = response.json()["user"]
        assert user["onboarding_completed"] is False


class TestLoginEndpoint:
    """Test user login endpoint"""

    def test_login_success(self, client, test_user):
        """Test successful login with correct credentials"""
        # Arrange
        credentials = {
            "email": test_user.email,
            "password": "ValidPass123!"  # From fixture
        }

        # Act
        response = client.post("/api/v1/auth/login", json=credentials)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_password(self, client, test_user):
        """Test login with incorrect password"""
        # Arrange
        credentials = {
            "email": test_user.email,
            "password": "WrongPassword123!"
        }

        # Act
        response = client.post("/api/v1/auth/login", json=credentials)

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_non_existent_user(self, client):
        """Test login with non-existent email"""
        # Arrange
        credentials = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        }

        # Act
        response = client.post("/api/v1/auth/login", json=credentials)

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_locked_account(self, client, locked_user):
        """Test login with locked account"""
        # Arrange
        credentials = {
            "email": locked_user.email,
            "password": "ValidPass123!"
        }

        # Act
        response = client.post("/api/v1/auth/login", json=credentials)

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "locked" in response.json()["detail"].lower()

    def test_login_increments_failed_attempts(self, client, test_user, db_session):
        """Test that failed login increments failed attempt counter"""
        # Arrange
        credentials = {
            "email": test_user.email,
            "password": "WrongPassword!"
        }
        initial_attempts = test_user.failed_login_attempts

        # Act
        response = client.post("/api/v1/auth/login", json=credentials)

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        db_session.refresh(test_user)
        assert test_user.failed_login_attempts == initial_attempts + 1

    def test_login_resets_failed_attempts_on_success(self, client, db_session, user_factory):
        """Test that successful login resets failed attempts"""
        # Arrange
        user = user_factory.create(
            db_session,
            email="resetuser@example.com",
            password="ValidPass123!",
            failed_login_attempts=3
        )

        credentials = {
            "email": user.email,
            "password": "ValidPass123!"
        }

        # Act
        response = client.post("/api/v1/auth/login", json=credentials)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        db_session.refresh(user)
        assert user.failed_login_attempts == 0

    def test_login_locks_account_after_max_attempts(self, client, test_user, db_session):
        """Test that account locks after max failed attempts"""
        # Arrange
        credentials = {
            "email": test_user.email,
            "password": "WrongPassword!"
        }

        # Act - Make 5 failed login attempts
        for i in range(5):
            response = client.post("/api/v1/auth/login", json=credentials)
            if i < 4:
                assert response.status_code == status.HTTP_401_UNAUTHORIZED
            else:
                # 5th attempt should lock account
                assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

        # Refresh user to check lockout
        db_session.refresh(test_user)

        # Assert
        assert test_user.failed_login_attempts >= 5
        assert test_user.locked_until is not None
        assert test_user.locked_until > datetime.utcnow()

    def test_login_case_insensitive_email(self, client, test_user):
        """Test that email is case-insensitive"""
        # Arrange
        credentials = {
            "email": test_user.email.upper(),  # Uppercase email
            "password": "ValidPass123!"
        }

        # Act
        response = client.post("/api/v1/auth/login", json=credentials)

        # Assert
        assert response.status_code == status.HTTP_200_OK

    def test_login_returns_valid_token(self, client, test_user):
        """Test that login returns a valid JWT token"""
        # Arrange
        credentials = {
            "email": test_user.email,
            "password": "ValidPass123!"
        }

        # Act
        response = client.post("/api/v1/auth/login", json=credentials)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        token = response.json()["access_token"]

        # Verify token works
        headers = {"Authorization": f"Bearer {token}"}
        me_response = client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == status.HTTP_200_OK


class TestGetCurrentUserEndpoint:
    """Test get current user endpoint"""

    def test_get_current_user_success(self, client, test_user, auth_headers):
        """Test getting current user with valid token"""
        # Act
        response = client.get("/api/v1/auth/me", headers=auth_headers)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
        assert "password" not in data
        assert "hashed_password" not in data

    def test_get_current_user_no_token(self, client):
        """Test getting current user without token"""
        # Act
        response = client.get("/api/v1/auth/me")

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        # Arrange
        headers = {"Authorization": "Bearer invalid_token"}

        # Act
        response = client.get("/api/v1/auth/me", headers=headers)

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_expired_token(self, client, expired_token):
        """Test getting current user with expired token"""
        # Arrange
        headers = {"Authorization": f"Bearer {expired_token}"}

        # Act
        response = client.get("/api/v1/auth/me", headers=headers)

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_malformed_header(self, client):
        """Test getting current user with malformed auth header"""
        # Arrange
        headers = {"Authorization": "InvalidFormat token123"}

        # Act
        response = client.get("/api/v1/auth/me", headers=headers)

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.api
class TestAuthEndpointsSecurity:
    """Security-focused tests for auth endpoints"""

    def test_login_rate_limiting(self, client, test_user):
        """Test that login endpoint is rate limited"""
        # Arrange
        credentials = {
            "email": test_user.email,
            "password": "WrongPassword!"
        }

        # Act - Make many requests rapidly
        responses = []
        for _ in range(10):
            response = client.post("/api/v1/auth/login", json=credentials)
            responses.append(response.status_code)

        # Assert - Should eventually hit rate limit
        assert status.HTTP_429_TOO_MANY_REQUESTS in responses

    def test_register_rate_limiting(self, client):
        """Test that register endpoint is rate limited"""
        # Arrange
        base_email = "ratelimit{}@example.com"

        # Act - Make many registration requests
        responses = []
        for i in range(5):
            user_data = {
                "email": base_email.format(i),
                "password": "SecurePass123!",
                "name": f"User {i}"
            }
            response = client.post("/api/v1/auth/register", json=user_data)
            responses.append(response.status_code)

        # Assert - Should eventually hit rate limit
        assert status.HTTP_429_TOO_MANY_REQUESTS in responses

    def test_password_not_in_response(self, client, test_user):
        """Test that password is never returned in responses"""
        # Arrange
        credentials = {
            "email": test_user.email,
            "password": "ValidPass123!"
        }

        # Act
        login_response = client.post("/api/v1/auth/login", json=credentials)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        me_response = client.get("/api/v1/auth/me", headers=headers)

        # Assert
        me_data = me_response.json()
        assert "password" not in str(me_data).lower()
        assert "hashed_password" not in str(me_data).lower()

    def test_lockout_prevents_brute_force(self, client, db_session, user_factory):
        """Test that account lockout prevents brute force attacks"""
        # Arrange
        user = user_factory.create(
            db_session,
            email="bruteforce@example.com",
            password="CorrectPass123!"
        )

        credentials = {
            "email": user.email,
            "password": "WrongPassword!"
        }

        # Act - Try to brute force
        for i in range(10):
            response = client.post("/api/v1/auth/login", json=credentials)

        # Assert - Account should be locked
        db_session.refresh(user)
        assert user.locked_until is not None

        # Even with correct password, should be locked
        correct_credentials = {
            "email": user.email,
            "password": "CorrectPass123!"
        }
        response = client.post("/api/v1/auth/login", json=correct_credentials)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_timing_attack_protection(self, client, test_user):
        """Test that response times don't leak user existence"""
        # This is a basic test - real timing attack tests need more sophisticated tooling
        # Arrange
        existing_email_creds = {
            "email": test_user.email,
            "password": "WrongPassword!"
        }

        non_existing_email_creds = {
            "email": "nonexistent@example.com",
            "password": "WrongPassword!"
        }

        # Act
        response1 = client.post("/api/v1/auth/login", json=existing_email_creds)
        response2 = client.post("/api/v1/auth/login", json=non_existing_email_creds)

        # Assert - Both should return 401 to not leak user existence
        assert response1.status_code == status.HTTP_401_UNAUTHORIZED
        assert response2.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("email,password,expected_status", [
    ("valid@example.com", "SecurePass123!", status.HTTP_201_CREATED),
    ("", "SecurePass123!", status.HTTP_422_UNPROCESSABLE_ENTITY),
    ("invalid-email", "SecurePass123!", status.HTTP_422_UNPROCESSABLE_ENTITY),
    ("valid@example.com", "weak", status.HTTP_422_UNPROCESSABLE_ENTITY),
    ("valid@example.com", "", status.HTTP_422_UNPROCESSABLE_ENTITY),
])
def test_register_validation_parametrized(client, email, password, expected_status):
    """Parametrized test for registration validation"""
    # Arrange
    user_data = {
        "email": email,
        "password": password,
        "name": "Test User"
    }

    # Act
    response = client.post("/api/v1/auth/register", json=user_data)

    # Assert
    assert response.status_code == expected_status
