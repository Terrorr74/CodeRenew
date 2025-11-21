# CodeRenew Backend Test Plan

## Overview
Detailed test specifications for all backend modules. Each test includes priority, acceptance criteria, mock requirements, and dependencies.

---

## 1. Security Module Tests

### File: `/backend/tests/unit/core/test_security.py`

#### Test 1.1: Password Hashing Verification
**Priority:** CRITICAL
**Category:** Unit Test
**Description:** Verify password hashing creates unique salts and is not reversible

```python
def test_password_hashing_creates_different_hashes_for_same_input():
    """Same password should produce different hashes (salt randomization)"""
    password = "SecurePassword123!"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)

    assert hash1 != hash2
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)

def test_password_verification_with_correct_password():
    """Correct password should verify against hash"""
    password = "MyPassword123!"
    hash = get_password_hash(password)
    assert verify_password(password, hash) is True

def test_password_verification_with_incorrect_password():
    """Incorrect password should not verify"""
    password = "CorrectPassword123!"
    wrong_password = "WrongPassword123!"
    hash = get_password_hash(password)
    assert verify_password(wrong_password, hash) is False

def test_password_hash_length_meets_bcrypt_standards():
    """Hash should be 60+ characters (bcrypt standard)"""
    password = "TestPassword123!"
    hash = get_password_hash(password)
    assert len(hash) >= 60
```

**Acceptance Criteria:**
- All 4 tests pass
- No plaintext passwords in code
- Bcrypt with cost factor 12+ used
- Performance < 500ms per hash

**Mocks:** None
**Dependencies:** `app.core.security`

---

#### Test 1.2: JWT Token Generation
**Priority:** CRITICAL
**Category:** Unit Test
**Description:** Verify JWT tokens are properly structured and contain required claims

```python
def test_create_access_token_returns_valid_jwt():
    """Token should be valid JWT with correct structure"""
    token = create_access_token(user_id=123)

    # Decode without verification to check structure
    decoded = jwt.decode(token, options={"verify_signature": False})

    assert decoded['sub'] == '123'  # user_id
    assert 'exp' in decoded
    assert 'iat' in decoded

def test_create_access_token_with_custom_expiration():
    """Token should respect custom expiration delta"""
    expires_delta = timedelta(hours=2)
    token = create_access_token(user_id=123, expires_delta=expires_delta)

    decoded = jwt.decode(token, options={"verify_signature": False})

    # Check expiration is approximately 2 hours from now
    expected_exp = int((datetime.utcnow() + expires_delta).timestamp())
    assert abs(decoded['exp'] - expected_exp) < 10  # 10 second tolerance

def test_access_token_default_expiration_is_24_hours():
    """Default token should expire in 24 hours"""
    token = create_access_token(user_id=123)
    decoded = jwt.decode(token, options={"verify_signature": False})

    now = int(datetime.utcnow().timestamp())
    exp = decoded['exp']

    # 24 hours = 86400 seconds (with 10 second tolerance)
    assert 86390 < (exp - now) < 86410
```

**Acceptance Criteria:**
- Tokens are valid JWT format
- All required claims present
- Expiration times respected
- Secret key properly used

**Mocks:** datetime (for expiration testing)
**Dependencies:** `app.core.security`, `python-jose`

---

#### Test 1.3: Token Validation
**Priority:** CRITICAL
**Category:** Unit Test
**Description:** Verify token validation works correctly for valid and invalid tokens

```python
def test_verify_token_with_valid_token():
    """Valid token should decode successfully"""
    token = create_access_token(user_id=123)
    user_id = verify_token(token)
    assert user_id == 123

def test_verify_token_with_expired_token(freezer):
    """Expired token should raise exception"""
    token = create_access_token(
        user_id=123,
        expires_delta=timedelta(hours=-1)  # Expired 1 hour ago
    )

    with pytest.raises(HTTPException) as exc_info:
        verify_token(token)

    assert exc_info.value.status_code == 401

def test_verify_token_with_invalid_signature():
    """Token with invalid signature should raise exception"""
    token = create_access_token(user_id=123)
    tampered_token = token[:-10] + 'xxxxxxxxxx'  # Modify signature

    with pytest.raises(HTTPException) as exc_info:
        verify_token(tampered_token)

    assert exc_info.value.status_code == 401

def test_verify_token_with_malformed_token():
    """Malformed token should raise exception"""
    with pytest.raises(HTTPException):
        verify_token("not.a.token")

    with pytest.raises(HTTPException):
        verify_token("invalid")

def test_verify_token_with_wrong_key_fails():
    """Token signed with different key should fail"""
    token = create_access_token(user_id=123, secret_key="correct_key")

    with patch('app.core.security.settings.SECRET_KEY', 'wrong_key'):
        with pytest.raises(HTTPException):
            verify_token(token)
```

**Acceptance Criteria:**
- Valid tokens decode
- Expired tokens rejected
- Tampered tokens rejected
- Malformed tokens rejected
- All errors return 401 status

**Mocks:** freezegun for time-based tests, settings patching
**Dependencies:** `app.core.security`, `python-jose`

---

## 2. Rate Limiting Tests

### File: `/backend/tests/unit/core/test_rate_limiting.py`

#### Test 2.1: Rate Limiter Configuration
**Priority:** HIGH
**Category:** Unit Test
**Description:** Verify rate limiter initializes with correct limits

```python
def test_rate_limiter_is_initialized():
    """Rate limiter should be available as dependency"""
    from app.core.rate_limiting import limiter
    assert limiter is not None

def test_register_rate_limit_is_configured():
    """Register endpoint should have rate limit configured"""
    from app.core.rate_limiting import REGISTER_RATE_LIMIT
    # Should be something like "5/hour"
    assert REGISTER_RATE_LIMIT is not None
    assert 'hour' in REGISTER_RATE_LIMIT

def test_login_rate_limit_is_more_strict_than_register():
    """Login should have stricter limit than register"""
    from app.core.rate_limiting import LOGIN_RATE_LIMIT, REGISTER_RATE_LIMIT

    login_limit = int(LOGIN_RATE_LIMIT.split('/')[0])
    register_limit = int(REGISTER_RATE_LIMIT.split('/')[0])

    assert login_limit <= register_limit
```

**Acceptance Criteria:**
- All endpoints have rate limits configured
- Limits follow security guidelines
- Login limit more strict than register

**Mocks:** None
**Dependencies:** `app.core.rate_limiting`

---

#### Test 2.2: Rate Limiting Enforcement
**Priority:** CRITICAL
**Category:** Integration Test
**Description:** Verify rate limits are enforced on endpoints

This is tested in integration tests (see section 5.1)

---

## 3. Password Policy Tests

### File: `/backend/tests/unit/core/test_password_policy.py`

#### Test 3.1: Password Validation
**Priority:** HIGH
**Category:** Unit Test
**Description:** Verify password meets security requirements

```python
def test_password_minimum_length_required():
    """Password must be at least 8 characters"""
    assert validate_password("short") is False
    assert validate_password("validpass123!") is True

def test_password_requires_uppercase():
    """Password must contain uppercase letter"""
    assert validate_password("validpass123!") is True
    assert validate_password("validpass123") is False

def test_password_requires_number():
    """Password must contain number"""
    assert validate_password("ValidPass!") is False
    assert validate_password("ValidPass123!") is True

def test_password_requires_special_character():
    """Password must contain special character"""
    assert validate_password("ValidPass123") is False
    assert validate_password("ValidPass123!") is True

def test_password_common_patterns_rejected():
    """Common passwords should be rejected"""
    weak_passwords = [
        "Password123!",
        "Qwerty123!",
        "Abc123456!"
    ]

    for pwd in weak_passwords:
        assert validate_password(pwd) is False
```

**Acceptance Criteria:**
- All validation rules enforced
- Clear error messages for each rule
- Performance < 100ms per validation

**Mocks:** None
**Dependencies:** Password validation service

---

## 4. User Model Tests

### File: `/backend/tests/unit/models/test_user.py`

#### Test 4.1: User Creation
**Priority:** HIGH
**Category:** Unit Test
**Description:** Verify user model can be instantiated with required fields

```python
def test_user_creation_with_required_fields(db_session):
    """User should be created with required fields"""
    user = User(
        email="test@example.com",
        hashed_password="$2b$12$...",
        name="Test User"
    )
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.is_verified is False
    assert user.onboarding_completed is False
    assert user.failed_login_attempts == 0

def test_user_creation_with_optional_fields(db_session):
    """User should accept optional fields"""
    user = User(
        email="test@example.com",
        hashed_password="$2b$12$...",
        name="Test User",
        company="Test Company"
    )
    db_session.add(user)
    db_session.commit()

    assert user.company == "Test Company"
```

**Acceptance Criteria:**
- User created with required fields
- Optional fields work correctly
- Default values applied
- Timestamps set correctly

**Mocks:** None
**Dependencies:** SQLAlchemy, User model

---

#### Test 4.2: User Relationships
**Priority:** HIGH
**Category:** Unit Test
**Description:** Verify user relationships to sites and scans

```python
def test_user_relationship_to_sites(db_session):
    """User should have relationship to sites"""
    user = UserFactory.create()
    site1 = SiteFactory.create(user=user)
    site2 = SiteFactory.create(user=user)

    db_session.refresh(user)
    assert len(user.sites) == 2
    assert site1 in user.sites
    assert site2 in user.sites

def test_user_relationship_to_scans(db_session):
    """User should have relationship to scans"""
    user = UserFactory.create()
    scan1 = ScanFactory.create(user=user)
    scan2 = ScanFactory.create(user=user)

    db_session.refresh(user)
    assert len(user.scans) == 2
    assert scan1 in user.scans
    assert scan2 in user.scans

def test_cascade_delete_removes_user_sites(db_session):
    """Deleting user should delete related sites"""
    user = UserFactory.create()
    site = SiteFactory.create(user=user)

    db_session.delete(user)
    db_session.commit()

    assert db_session.query(Site).filter_by(id=site.id).first() is None

def test_cascade_delete_removes_user_scans(db_session):
    """Deleting user should delete related scans"""
    user = UserFactory.create()
    scan = ScanFactory.create(user=user)

    db_session.delete(user)
    db_session.commit()

    assert db_session.query(Scan).filter_by(id=scan.id).first() is None
```

**Acceptance Criteria:**
- Relationships work correctly
- Cascade delete works
- Foreign key constraints enforced

**Mocks:** None
**Dependencies:** SQLAlchemy, User/Site/Scan models, factories

---

#### Test 4.3: Unique Email Constraint
**Priority:** HIGH
**Category:** Unit Test
**Description:** Verify email uniqueness is enforced

```python
def test_duplicate_email_raises_integrity_error(db_session):
    """Duplicate email should raise integrity error"""
    user1 = UserFactory.create(email="duplicate@example.com")

    with pytest.raises(IntegrityError):
        user2 = User(
            email="duplicate@example.com",
            hashed_password="$2b$12$...",
            name="Another User"
        )
        db_session.add(user2)
        db_session.commit()

def test_email_is_indexed():
    """Email column should be indexed for performance"""
    # Check index exists on User.email
    email_column = User.__table__.columns['email']
    assert email_column.index or any(
        idx.expressions[0].name == 'email'
        for idx in User.__table__.indexes
    )
```

**Acceptance Criteria:**
- Duplicate emails prevented
- Email indexed for queries
- Clear error messages

**Mocks:** None
**Dependencies:** SQLAlchemy, User model

---

#### Test 4.4: Timestamp Fields
**Priority:** MEDIUM
**Category:** Unit Test
**Description:** Verify created_at and updated_at work correctly

```python
@freeze_time("2024-01-01 12:00:00")
def test_created_at_timestamp_set_on_creation(db_session):
    """created_at should be set when user is created"""
    user = UserFactory.create()
    assert user.created_at is not None
    assert user.created_at.replace(microsecond=0) == datetime(2024, 1, 1, 12, 0, 0)

@freeze_time("2024-01-01 12:00:00")
def test_updated_at_timestamp_updated_on_modification(db_session):
    """updated_at should update when user is modified"""
    user = UserFactory.create()
    initial_updated = user.updated_at

    # Wait 1 hour
    with freeze_time("2024-01-01 13:00:00"):
        user.name = "Updated Name"
        db_session.commit()
        db_session.refresh(user)

        assert user.updated_at > initial_updated
```

**Acceptance Criteria:**
- Timestamps set correctly
- Timestamps use server time
- Update timestamps reflect changes

**Mocks:** freezegun for time control
**Dependencies:** SQLAlchemy, User model

---

## 5. Authentication Endpoint Tests

### File: `/backend/tests/integration/test_auth_flows.py`

#### Test 5.1: User Registration Flow
**Priority:** CRITICAL
**Category:** Integration Test
**Description:** Complete registration workflow with validation

```python
def test_register_with_valid_data_creates_user_and_returns_token(client, db_session):
    """Valid registration should create user and return token"""
    response = client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "SecurePass123!",
        "name": "New User"
    })

    assert response.status_code == 201
    data = response.json()

    assert "access_token" in data
    assert "user" in data
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["name"] == "New User"
    assert data["user"]["is_verified"] is False

    # Verify user created in database
    user = db_session.query(User).filter_by(email="newuser@example.com").first()
    assert user is not None
    assert user.name == "New User"

def test_register_with_duplicate_email_returns_400(client, db_session):
    """Duplicate email should return 400"""
    UserFactory.create(email="existing@example.com")

    response = client.post("/api/v1/auth/register", json={
        "email": "existing@example.com",
        "password": "SecurePass123!",
        "name": "Another User"
    })

    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_register_with_weak_password_returns_422(client):
    """Weak password should return validation error"""
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "weak",
        "name": "Test User"
    })

    assert response.status_code == 422

def test_register_missing_required_field_returns_422(client):
    """Missing required field should return validation error"""
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com"
        # Missing password and name
    })

    assert response.status_code == 422

def test_register_with_invalid_email_returns_422(client):
    """Invalid email should return validation error"""
    response = client.post("/api/v1/auth/register", json={
        "email": "not-an-email",
        "password": "SecurePass123!",
        "name": "Test User"
    })

    assert response.status_code == 422

def test_register_is_rate_limited(client):
    """Register endpoint should be rate limited"""
    # Make 6 registration attempts (limit is typically 5/hour)
    for i in range(6):
        response = client.post("/api/v1/auth/register", json={
            "email": f"user{i}@example.com",
            "password": "SecurePass123!",
            "name": f"User {i}"
        })

        if i < 5:
            assert response.status_code in [201, 400]  # Success or duplicate
        else:
            assert response.status_code == 429  # Rate limited

def test_register_returns_token_with_correct_claims(client, db_session):
    """Returned token should have correct claims"""
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!",
        "name": "Test User"
    })

    token = response.json()["access_token"]
    decoded = jwt.decode(token, options={"verify_signature": False})

    user = db_session.query(User).filter_by(email="test@example.com").first()
    assert decoded['sub'] == str(user.id)
```

**Acceptance Criteria:**
- Valid registration creates user
- Token returned and valid
- Validation enforced
- Rate limiting applied
- Database consistent
- Response time < 500ms

**Mocks:** Email service (if async)
**Dependencies:** Database, auth client, factories

---

#### Test 5.2: User Login Flow
**Priority:** CRITICAL
**Category:** Integration Test
**Description:** Login with valid and invalid credentials

```python
def test_login_with_valid_credentials_returns_token(client, db_session):
    """Valid credentials should return token"""
    user = UserFactory.create(
        email="testuser@example.com",
        hashed_password=get_password_hash("MyPassword123!")
    )

    response = client.post("/api/v1/auth/login", json={
        "email": "testuser@example.com",
        "password": "MyPassword123!"
    })

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["user"]["email"] == "testuser@example.com"

def test_login_with_wrong_password_returns_401(client):
    """Wrong password should return 401"""
    UserFactory.create(
        email="testuser@example.com",
        hashed_password=get_password_hash("CorrectPassword123!")
    )

    response = client.post("/api/v1/auth/login", json={
        "email": "testuser@example.com",
        "password": "WrongPassword123!"
    })

    assert response.status_code == 401

def test_login_with_nonexistent_user_returns_401(client):
    """Non-existent user should return 401"""
    response = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "SomePassword123!"
    })

    assert response.status_code == 401

def test_failed_login_increments_counter(client, db_session):
    """Failed login should increment failed_login_attempts"""
    user = UserFactory.create(
        email="testuser@example.com",
        hashed_password=get_password_hash("CorrectPassword123!")
    )

    # Wrong password
    client.post("/api/v1/auth/login", json={
        "email": "testuser@example.com",
        "password": "WrongPassword123!"
    })

    db_session.refresh(user)
    assert user.failed_login_attempts == 1

def test_successful_login_resets_failed_counter(client, db_session):
    """Successful login should reset failed_login_attempts to 0"""
    user = UserFactory.create(
        email="testuser@example.com",
        hashed_password=get_password_hash("CorrectPassword123!"),
        failed_login_attempts=3
    )

    response = client.post("/api/v1/auth/login", json={
        "email": "testuser@example.com",
        "password": "CorrectPassword123!"
    })

    assert response.status_code == 200

    db_session.refresh(user)
    assert user.failed_login_attempts == 0

def test_login_is_rate_limited(client):
    """Login should be rate limited"""
    user = UserFactory.create()

    # Make 11 attempts (limit is typically 10/hour)
    for i in range(11):
        response = client.post("/api/v1/auth/login", json={
            "email": user.email,
            "password": "WrongPassword123!"
        })

        if i < 10:
            assert response.status_code == 401
        else:
            assert response.status_code == 429
```

**Acceptance Criteria:**
- Valid login returns token
- Invalid credentials return 401
- Failed attempts tracked
- Rate limiting enforced
- Counter resets on success
- Response time < 500ms

**Mocks:** None
**Dependencies:** Database, auth client, factories, security utilities

---

#### Test 5.3: Account Lockout Flow
**Priority:** CRITICAL
**Category:** Integration Test
**Description:** Account locks after N failed attempts and unlocks after duration

```python
def test_account_locks_after_max_failed_attempts(client, db_session):
    """Account should lock after 5 failed login attempts"""
    user = UserFactory.create(
        email="testuser@example.com",
        hashed_password=get_password_hash("CorrectPassword123!")
    )

    # Make 5 failed attempts
    for i in range(5):
        response = client.post("/api/v1/auth/login", json={
            "email": "testuser@example.com",
            "password": "WrongPassword123!"
        })
        assert response.status_code == 401

    # Verify account locked
    db_session.refresh(user)
    assert user.locked_until is not None

def test_locked_account_cannot_login(client):
    """Locked account should not login even with correct password"""
    now = datetime.utcnow()
    user = UserFactory.create(
        email="testuser@example.com",
        hashed_password=get_password_hash("CorrectPassword123!"),
        locked_until=now + timedelta(minutes=30)
    )

    response = client.post("/api/v1/auth/login", json={
        "email": "testuser@example.com",
        "password": "CorrectPassword123!"
    })

    assert response.status_code == 403
    assert "account is locked" in response.json()["detail"].lower()

def test_locked_account_unlocks_after_duration(client, db_session):
    """Account should unlock after lockout duration expires"""
    lock_time = datetime.utcnow()
    user = UserFactory.create(
        email="testuser@example.com",
        hashed_password=get_password_hash("CorrectPassword123!"),
        locked_until=lock_time + timedelta(minutes=30)
    )

    # Try to login while locked
    response = client.post("/api/v1/auth/login", json={
        "email": "testuser@example.com",
        "password": "CorrectPassword123!"
    })
    assert response.status_code == 403

    # Advance time 31 minutes
    with freeze_time(lock_time + timedelta(minutes=31)):
        response = client.post("/api/v1/auth/login", json={
            "email": "testuser@example.com",
            "password": "CorrectPassword123!"
        })
        assert response.status_code == 200

def test_lockout_message_differs_from_wrong_password(client):
    """Locked account message should differ from wrong password"""
    user = UserFactory.create(
        email="testuser@example.com",
        hashed_password=get_password_hash("CorrectPassword123!"),
        locked_until=datetime.utcnow() + timedelta(minutes=30)
    )

    response = client.post("/api/v1/auth/login", json={
        "email": "testuser@example.com",
        "password": "CorrectPassword123!"
    })

    assert response.status_code == 403
    detail = response.json()["detail"]
    assert "locked" in detail.lower()
    assert "invalid" not in detail.lower()
```

**Acceptance Criteria:**
- Lock after 5 failed attempts
- Cannot login while locked (even correct password)
- Automatic unlock after 30 minutes
- Lockout message differs from wrong password
- Clear user communication

**Mocks:** freezegun for time control
**Dependencies:** Database, auth client, factories, security utilities

---

#### Test 5.4: Password Reset Flow
**Priority:** CRITICAL
**Category:** Integration Test
**Description:** Request reset, verify token, and reset password

```python
def test_password_reset_request_creates_token(client, db_session, mock_email):
    """Password reset request should create reset token"""
    user = UserFactory.create(email="testuser@example.com")

    response = client.post("/api/v1/auth/request-password-reset", json={
        "email": "testuser@example.com"
    })

    assert response.status_code == 200

    db_session.refresh(user)
    assert user.reset_token is not None
    assert user.reset_token_expires is not None

def test_password_reset_email_sent(client, mock_email):
    """Password reset email should be sent"""
    user = UserFactory.create(email="testuser@example.com")

    client.post("/api/v1/auth/request-password-reset", json={
        "email": "testuser@example.com"
    })

    mock_email.assert_called_once()
    call_args = mock_email.call_args
    assert user.email in call_args[0] or call_args[1].get('to') == user.email

def test_password_reset_token_expires(client, db_session):
    """Reset token should expire after 1 hour"""
    user = UserFactory.create(email="testuser@example.com")
    reset_time = datetime.utcnow()
    user.reset_token = "valid_token"
    user.reset_token_expires = reset_time + timedelta(hours=1)
    db_session.commit()

    # Token valid at 59 minutes
    with freeze_time(reset_time + timedelta(minutes=59)):
        response = client.post("/api/v1/auth/reset-password", json={
            "token": "valid_token",
            "new_password": "NewPassword123!"
        })
        assert response.status_code == 200

    # Token expired at 61 minutes
    with freeze_time(reset_time + timedelta(minutes=61)):
        response = client.post("/api/v1/auth/reset-password", json={
            "token": "valid_token",
            "new_password": "NewPassword123!"
        })
        assert response.status_code == 400

def test_reset_token_single_use_only(client, db_session):
    """Reset token should only work once"""
    user = UserFactory.create(email="testuser@example.com")
    reset_time = datetime.utcnow()
    user.reset_token = "one_time_token"
    user.reset_token_expires = reset_time + timedelta(hours=1)
    db_session.commit()

    # First use succeeds
    response = client.post("/api/v1/auth/reset-password", json={
        "token": "one_time_token",
        "new_password": "NewPassword123!"
    })
    assert response.status_code == 200

    # Second use fails
    response = client.post("/api/v1/auth/reset-password", json={
        "token": "one_time_token",
        "new_password": "AnotherPassword123!"
    })
    assert response.status_code == 400

def test_password_changed_after_reset(client, db_session):
    """User should be able to login with new password"""
    user = UserFactory.create(
        email="testuser@example.com",
        hashed_password=get_password_hash("OldPassword123!")
    )
    reset_time = datetime.utcnow()
    user.reset_token = "valid_token"
    user.reset_token_expires = reset_time + timedelta(hours=1)
    db_session.commit()

    # Reset password
    response = client.post("/api/v1/auth/reset-password", json={
        "token": "valid_token",
        "new_password": "NewPassword123!"
    })
    assert response.status_code == 200

    # Old password doesn't work
    response = client.post("/api/v1/auth/login", json={
        "email": "testuser@example.com",
        "password": "OldPassword123!"
    })
    assert response.status_code == 401

    # New password works
    response = client.post("/api/v1/auth/login", json={
        "email": "testuser@example.com",
        "password": "NewPassword123!"
    })
    assert response.status_code == 200

def test_invalid_reset_token_returns_400(client):
    """Invalid reset token should return 400"""
    response = client.post("/api/v1/auth/reset-password", json={
        "token": "invalid_token",
        "new_password": "NewPassword123!"
    })

    assert response.status_code == 400

def test_password_reset_is_rate_limited(client):
    """Password reset requests should be rate limited"""
    user = UserFactory.create(email="testuser@example.com")

    # Make 4 requests (limit is typically 3/hour)
    for i in range(4):
        response = client.post("/api/v1/auth/request-password-reset", json={
            "email": "testuser@example.com"
        })

        if i < 3:
            assert response.status_code == 200
        else:
            assert response.status_code == 429
```

**Acceptance Criteria:**
- Reset token created and sent
- Token expires after 1 hour
- Token single-use only
- Password updated in database
- Old password invalid after reset
- New password valid immediately
- Rate limiting enforced

**Mocks:** Email service, freezegun for time control
**Dependencies:** Database, auth client, factories, email service

---

## 6. Scan Processing Tests

### File: `/backend/tests/integration/test_scan_workflows.py`

#### Test 6.1: File Upload and Scan Creation
**Priority:** CRITICAL
**Category:** Integration Test
**Description:** Upload ZIP file and create scan record

```python
def test_upload_wordpress_theme_creates_scan_record(
    authenticated_client, db_session, sample_theme_zip
):
    """Uploading theme ZIP should create scan record"""
    response = authenticated_client.post(
        "/api/v1/scans/upload",
        files={"file": sample_theme_zip},
        data={"wordpress_version_from": "5.0", "wordpress_version_to": "6.0"}
    )

    assert response.status_code == 202  # Accepted (async)
    data = response.json()

    assert "scan_id" in data

    # Verify scan in database
    scan = db_session.query(Scan).filter_by(id=data["scan_id"]).first()
    assert scan is not None
    assert scan.status == ScanStatus.PENDING
    assert scan.user_id == authenticated_client.user.id

def test_upload_without_authentication_returns_401(client, sample_theme_zip):
    """Unauthenticated upload should return 401"""
    response = client.post(
        "/api/v1/scans/upload",
        files={"file": sample_theme_zip},
        data={"wordpress_version_from": "5.0", "wordpress_version_to": "6.0"}
    )

    assert response.status_code == 401

def test_upload_invalid_file_returns_400(authenticated_client):
    """Invalid file should return 400"""
    response = authenticated_client.post(
        "/api/v1/scans/upload",
        files={"file": ("test.txt", b"not a zip file")},
        data={"wordpress_version_from": "5.0", "wordpress_version_to": "6.0"}
    )

    assert response.status_code == 400

def test_upload_missing_version_info_returns_422(authenticated_client, sample_theme_zip):
    """Missing version info should return 422"""
    response = authenticated_client.post(
        "/api/v1/scans/upload",
        files={"file": sample_theme_zip}
        # Missing wordpress_version_from and wordpress_version_to
    )

    assert response.status_code == 422

def test_uploaded_file_stored_correctly(authenticated_client, db_session, sample_theme_zip):
    """Uploaded file should be stored in correct location"""
    response = authenticated_client.post(
        "/api/v1/scans/upload",
        files={"file": sample_theme_zip},
        data={"wordpress_version_from": "5.0", "wordpress_version_to": "6.0"}
    )

    scan_id = response.json()["scan_id"]
    scan = db_session.query(Scan).filter_by(id=scan_id).first()

    # Verify file exists at expected location
    upload_dir = Path(settings.UPLOAD_DIR) / str(scan.user_id) / str(scan_id)
    zip_files = list(upload_dir.glob("*.zip"))
    assert len(zip_files) == 1
```

**Acceptance Criteria:**
- File uploaded successfully
- Scan record created
- File stored securely
- Async processing started
- Response time < 2 seconds

**Mocks:** None
**Dependencies:** Database, file storage, authenticated client

---

#### Test 6.2: Scan Processing Status
**Priority:** HIGH
**Category:** Integration Test
**Description:** Track scan processing status transitions

```python
def test_scan_status_transitions_correctly(authenticated_client, db_session):
    """Scan status should transition from PENDING -> PROCESSING -> COMPLETED"""
    # Create scan
    response = authenticated_client.post(
        "/api/v1/scans/upload",
        files={"file": sample_theme_zip},
        data={"wordpress_version_from": "5.0", "wordpress_version_to": "6.0"}
    )
    scan_id = response.json()["scan_id"]

    scan = db_session.query(Scan).filter_by(id=scan_id).first()
    assert scan.status == ScanStatus.PENDING

    # Simulate processing
    scan.status = ScanStatus.PROCESSING
    db_session.commit()

    # Verify status endpoint
    response = authenticated_client.get(f"/api/v1/scans/{scan_id}")
    assert response.json()["status"] == ScanStatus.PROCESSING

def test_scan_results_available_when_complete(authenticated_client, db_session):
    """Completed scan should have results"""
    scan = ScanFactory.create(
        user=authenticated_client.user,
        status=ScanStatus.COMPLETED
    )
    ScanResultFactory.create(scan=scan, severity="critical")
    ScanResultFactory.create(scan=scan, severity="warning")

    response = authenticated_client.get(f"/api/v1/scans/{scan.id}/results")

    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
```

**Acceptance Criteria:**
- Status transitions correctly
- Results available when complete
- User can retrieve results
- Proper error on non-existent scan

**Mocks:** None
**Dependencies:** Database, scan factories

---

## 7. Additional Critical Paths

### File: `/backend/tests/integration/test_payment_flows.py`

#### Test 7.1: Payment Intent Creation
**Priority:** CRITICAL
**Category:** Integration Test

```python
def test_create_payment_intent_for_subscription(authenticated_client, db_session):
    """Creating payment intent should work correctly"""
    response = authenticated_client.post("/api/v1/orders/create-payment", json={
        "plan_id": "plan_monthly",
        "plan_name": "Monthly Plan",
        "amount": 2999
    })

    assert response.status_code == 200
    data = response.json()

    assert "client_secret" in data
    assert "payment_intent_id" in data

    # Verify order created in database
    order = db_session.query(Order).filter_by(
        stripe_payment_intent_id=data["payment_intent_id"]
    ).first()
    assert order is not None
```

**Acceptance Criteria:**
- Payment intent created
- Client secret returned
- Order record created
- Amount correct

**Mocks:** Stripe API (test mode)
**Dependencies:** Database, Stripe integration, authenticated client

---

## 8. Test Execution Commands

```bash
# Run all unit tests
pytest backend/tests/unit -v --cov=app --cov-report=html

# Run all integration tests
pytest backend/tests/integration -v

# Run specific test file
pytest backend/tests/unit/core/test_security.py -v

# Run with parallel execution
pytest backend/tests/unit -n auto

# Run with detailed output
pytest backend/tests/integration/test_auth_flows.py -v -s

# Run with markers
pytest -m critical -v  # Run tests marked as critical

# Generate coverage report
pytest --cov=app --cov-report=html --cov-report=term-missing
```

---

## 9. Pytest Configuration

### File: `/backend/pytest.ini`

```ini
[pytest]
testpaths = backend/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
markers =
    critical: critical path tests
    unit: unit tests
    integration: integration tests
    e2e: end-to-end tests
timeout = 300
```

---

## 10. Test Dependencies Matrix

| Module | Unit | Integration | E2E | Dependencies |
|--------|------|-------------|-----|--------------|
| Security | ✓ | - | - | pytest, freezegun |
| Auth | ✓ | ✓ | ✓ | Database, email mock |
| Rate Limiting | ✓ | ✓ | - | slowapi, client |
| Account Lockout | ✓ | ✓ | ✓ | Database, time mock |
| Scan Processing | - | ✓ | ✓ | File storage, Claude mock |
| Payment | - | ✓ | ✓ | Stripe test mode |

---

**Document Version:** 1.0
**Last Updated:** 2024-11-20
**Status:** Ready for Implementation
