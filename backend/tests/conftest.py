"""
Pytest configuration and shared fixtures
Provides database, authentication, and mock fixtures for all tests
"""
import os
import sys
from datetime import datetime, timedelta
from typing import Generator, AsyncGenerator
from unittest.mock import MagicMock, AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment variables BEFORE importing app modules
os.environ["TESTING"] = "true"
os.environ["ALLOWED_ORIGINS"] = '["http://localhost:3000"]'
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test_secret_key_min_32_chars_long_for_jwt"
os.environ["ANTHROPIC_API_KEY"] = "test_anthropic_api_key"
os.environ["STRIPE_SECRET_KEY"] = "sk_test_fake_stripe_key"
os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_test_fake_webhook_secret"
os.environ["RESEND_API_KEY"] = "re_test_fake_resend_key"
os.environ["WORDPRESS_MCP_ENABLED"] = "false"

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.models.base import Base
from app.models.user import User
from app.models.site import Site
from app.models.scan import Scan
from app.models.order import Order
from app.db.session import get_db


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def engine():
    """
    Create an in-memory SQLite engine for testing
    Using StaticPool to share the connection across threads
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    """
    Create a new database session for a test
    Automatically rolls back after test to maintain isolation
    """
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """
    Create a TestClient with database session override
    """
    from app.main import app

    # Override the get_db dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides
    app.dependency_overrides.clear()


# ============================================================================
# User Factories and Fixtures
# ============================================================================

class UserFactory:
    """Factory for creating test users"""

    @staticmethod
    def create(
        db: Session,
        email: str = "test@example.com",
        password: str = "TestPass123!",
        name: str = "Test User",
        company: str = None,
        is_verified: bool = True,
        onboarding_completed: bool = True,
        **kwargs
    ) -> User:
        """Create a user in the database"""
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            name=name,
            company=company,
            is_verified=is_verified,
            onboarding_completed=onboarding_completed,
            **kwargs
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def build(**kwargs) -> User:
        """Build a user without saving to database"""
        defaults = {
            "email": "test@example.com",
            "hashed_password": get_password_hash("TestPass123!"),
            "name": "Test User",
            "is_verified": True,
            "onboarding_completed": True,
        }
        defaults.update(kwargs)
        return User(**defaults)


@pytest.fixture
def user_factory():
    """Provide UserFactory to tests"""
    return UserFactory


@pytest.fixture
def test_user(db_session) -> User:
    """Create a standard test user"""
    return UserFactory.create(
        db_session,
        email="testuser@example.com",
        password="ValidPass123!",
        name="Test User"
    )


@pytest.fixture
def admin_user(db_session) -> User:
    """Create an admin test user"""
    return UserFactory.create(
        db_session,
        email="admin@example.com",
        password="AdminPass123!",
        name="Admin User"
    )


@pytest.fixture
def unverified_user(db_session) -> User:
    """Create an unverified test user"""
    return UserFactory.create(
        db_session,
        email="unverified@example.com",
        password="ValidPass123!",
        name="Unverified User",
        is_verified=False,
        verification_token="test_verification_token"
    )


@pytest.fixture
def locked_user(db_session) -> User:
    """Create a locked-out test user"""
    return UserFactory.create(
        db_session,
        email="locked@example.com",
        password="ValidPass123!",
        name="Locked User",
        failed_login_attempts=5,
        locked_until=datetime.utcnow() + timedelta(minutes=30),
        last_failed_login=datetime.utcnow()
    )


# ============================================================================
# Site and Scan Factories
# ============================================================================

class SiteFactory:
    """Factory for creating test sites"""

    @staticmethod
    def create(
        db: Session,
        user: User,
        url: str = "https://example.com",
        name: str = "Test Site",
        **kwargs
    ) -> Site:
        """Create a site in the database"""
        site = Site(
            user_id=user.id,
            url=url,
            name=name,
            **kwargs
        )
        db.add(site)
        db.commit()
        db.refresh(site)
        return site


class ScanFactory:
    """Factory for creating test scans"""

    @staticmethod
    def create(
        db: Session,
        user: User,
        site: Site = None,
        status: str = "pending",
        **kwargs
    ) -> Scan:
        """Create a scan in the database"""
        scan = Scan(
            user_id=user.id,
            site_id=site.id if site else None,
            status=status,
            **kwargs
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)
        return scan


@pytest.fixture
def site_factory():
    """Provide SiteFactory to tests"""
    return SiteFactory


@pytest.fixture
def scan_factory():
    """Provide ScanFactory to tests"""
    return ScanFactory


@pytest.fixture
def test_site(db_session, test_user) -> Site:
    """Create a standard test site"""
    return SiteFactory.create(
        db_session,
        test_user,
        url="https://testsite.com",
        name="Test WordPress Site"
    )


@pytest.fixture
def test_scan(db_session, test_user, test_site) -> Scan:
    """Create a standard test scan"""
    return ScanFactory.create(
        db_session,
        test_user,
        test_site,
        status="pending"
    )


# ============================================================================
# Authentication Fixtures
# ============================================================================

@pytest.fixture
def test_token(test_user) -> str:
    """Create a valid JWT token for test user"""
    return create_access_token(data={"sub": test_user.email})


@pytest.fixture
def admin_token(admin_user) -> str:
    """Create a valid JWT token for admin user"""
    return create_access_token(data={"sub": admin_user.email})


@pytest.fixture
def expired_token() -> str:
    """Create an expired JWT token"""
    return create_access_token(
        data={"sub": "test@example.com"},
        expires_delta=timedelta(seconds=-1)
    )


@pytest.fixture
def auth_headers(test_token) -> dict:
    """Create authorization headers with valid token"""
    return {"Authorization": f"Bearer {test_token}"}


# ============================================================================
# Mock External Services
# ============================================================================

@pytest.fixture
def mock_anthropic_client(mocker):
    """Mock Anthropic Claude API client"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(text="Mock Claude response with compatibility analysis")
    ]
    mock_client.messages.create.return_value = mock_response

    mocker.patch("app.services.claude.client.Anthropic", return_value=mock_client)
    return mock_client


@pytest.fixture
def mock_stripe(mocker):
    """Mock Stripe API"""
    mock_stripe = MagicMock()

    # Mock checkout session creation
    mock_session = MagicMock()
    mock_session.id = "cs_test_123"
    mock_session.url = "https://checkout.stripe.com/test"
    mock_stripe.checkout.Session.create.return_value = mock_session

    # Mock webhook construction
    mock_stripe.Webhook.construct_event.return_value = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "metadata": {"user_id": "1"}
            }
        }
    }

    mocker.patch("stripe.checkout.Session", mock_stripe.checkout.Session)
    mocker.patch("stripe.Webhook", mock_stripe.Webhook)
    return mock_stripe


@pytest.fixture
def mock_resend(mocker):
    """Mock Resend email service"""
    mock_resend = MagicMock()
    mock_response = {"id": "email_test_123"}
    mock_resend.Emails.send.return_value = mock_response

    mocker.patch("app.services.email.resend", mock_resend)
    return mock_resend


@pytest.fixture
def mock_wordpress_scanner(mocker):
    """Mock WordPress scanner service"""
    mock_scanner = AsyncMock()
    mock_scanner.scan_code.return_value = {
        "status": "completed",
        "issues": [],
        "compatibility_score": 95
    }

    mocker.patch(
        "app.services.wordpress.scanner.WordPressScanner",
        return_value=mock_scanner
    )
    return mock_scanner


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_php_code() -> str:
    """Sample PHP code for testing"""
    return """<?php
/**
 * Plugin Name: Test Plugin
 * Version: 1.0.0
 */

function test_deprecated_function() {
    // Using deprecated function
    $posts = get_posts();
    return $posts;
}

add_action('init', 'test_deprecated_function');
"""


@pytest.fixture
def sample_wordpress_file_structure() -> dict:
    """Sample WordPress file structure for testing"""
    return {
        "wp-content/themes/mytheme/": {
            "style.css": "/* Theme styles */",
            "functions.php": "<?php // Theme functions",
            "index.php": "<?php get_header(); ?>",
        },
        "wp-content/plugins/myplugin/": {
            "plugin.php": "<?php /* Plugin code */",
        }
    }


@pytest.fixture
def sample_scan_results() -> dict:
    """Sample scan results for testing"""
    return {
        "compatibility_score": 85,
        "issues": [
            {
                "type": "deprecated_function",
                "severity": "high",
                "file": "functions.php",
                "line": 42,
                "message": "Function get_posts() is deprecated",
                "replacement": "Use WP_Query instead"
            }
        ],
        "summary": {
            "total_files": 15,
            "files_scanned": 15,
            "issues_found": 1,
            "high_severity": 1,
            "medium_severity": 0,
            "low_severity": 0
        }
    }


# ============================================================================
# Settings and Configuration
# ============================================================================

@pytest.fixture(autouse=True)
def reset_rate_limits():
    """Reset rate limiting between tests"""
    from app.core.rate_limiting import limiter
    if hasattr(limiter, '_storage'):
        limiter._storage.reset()


@pytest.fixture
def test_settings():
    """Provide test settings"""
    return settings
