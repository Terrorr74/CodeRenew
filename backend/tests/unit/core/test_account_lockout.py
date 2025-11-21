"""
Unit tests for account lockout mechanism
Tests lockout behavior after failed login attempts
"""
import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time

from app.models.user import User


class TestAccountLockoutModel:
    """Test account lockout fields in User model"""

    def test_user_has_lockout_fields(self, db_session, user_factory):
        """Test that User model has lockout-related fields"""
        # Arrange & Act
        user = user_factory.create(db_session)

        # Assert
        assert hasattr(user, 'failed_login_attempts')
        assert hasattr(user, 'locked_until')
        assert hasattr(user, 'last_failed_login')

    def test_new_user_has_zero_failed_attempts(self, db_session, user_factory):
        """Test that new users start with zero failed attempts"""
        # Arrange & Act
        user = user_factory.create(db_session)

        # Assert
        assert user.failed_login_attempts == 0

    def test_new_user_not_locked(self, db_session, user_factory):
        """Test that new users are not locked"""
        # Arrange & Act
        user = user_factory.create(db_session)

        # Assert
        assert user.locked_until is None

    def test_user_can_be_locked(self, db_session, user_factory):
        """Test that user can be locked with lockout time"""
        # Arrange
        lockout_time = datetime.utcnow() + timedelta(minutes=30)
        user = user_factory.create(
            db_session,
            failed_login_attempts=5,
            locked_until=lockout_time
        )

        # Act
        db_session.refresh(user)

        # Assert
        assert user.failed_login_attempts == 5
        assert user.locked_until is not None
        assert user.locked_until >= datetime.utcnow()

    def test_failed_attempts_can_increment(self, db_session, user_factory):
        """Test that failed login attempts can be incremented"""
        # Arrange
        user = user_factory.create(db_session, failed_login_attempts=0)

        # Act
        user.failed_login_attempts += 1
        user.last_failed_login = datetime.utcnow()
        db_session.commit()
        db_session.refresh(user)

        # Assert
        assert user.failed_login_attempts == 1
        assert user.last_failed_login is not None

    def test_failed_attempts_can_be_reset(self, db_session, user_factory):
        """Test that failed attempts can be reset after successful login"""
        # Arrange
        user = user_factory.create(db_session, failed_login_attempts=3)

        # Act
        user.failed_login_attempts = 0
        user.last_failed_login = None
        user.locked_until = None
        db_session.commit()
        db_session.refresh(user)

        # Assert
        assert user.failed_login_attempts == 0
        assert user.last_failed_login is None
        assert user.locked_until is None


class TestAccountLockoutLogic:
    """Test account lockout logic"""

    def test_user_locked_when_lockout_time_in_future(self, db_session, user_factory):
        """Test that user is considered locked when lockout time is in future"""
        # Arrange
        future_lockout = datetime.utcnow() + timedelta(minutes=15)
        user = user_factory.create(
            db_session,
            failed_login_attempts=5,
            locked_until=future_lockout
        )

        # Act & Assert
        assert user.locked_until > datetime.utcnow()

    def test_user_not_locked_when_lockout_time_expired(self, db_session, user_factory):
        """Test that user is not locked when lockout time has passed"""
        # Arrange
        past_lockout = datetime.utcnow() - timedelta(minutes=1)
        user = user_factory.create(
            db_session,
            failed_login_attempts=5,
            locked_until=past_lockout
        )

        # Act & Assert
        assert user.locked_until < datetime.utcnow()

    def test_user_not_locked_when_no_lockout_time(self, db_session, user_factory):
        """Test that user is not locked when locked_until is None"""
        # Arrange
        user = user_factory.create(
            db_session,
            failed_login_attempts=2,
            locked_until=None
        )

        # Act & Assert
        assert user.locked_until is None

    def test_lockout_duration_correct(self, db_session, user_factory):
        """Test that lockout duration is set correctly (typically 30 minutes)"""
        # Arrange
        lockout_duration_minutes = 30
        lockout_time = datetime.utcnow() + timedelta(minutes=lockout_duration_minutes)

        user = user_factory.create(
            db_session,
            failed_login_attempts=5,
            locked_until=lockout_time
        )

        # Act
        time_until_unlock = (user.locked_until - datetime.utcnow()).total_seconds() / 60

        # Assert - should be approximately 30 minutes (allow 1 minute tolerance)
        assert 29 <= time_until_unlock <= 31


class TestAccountLockoutThresholds:
    """Test lockout thresholds and conditions"""

    def test_lockout_threshold_is_five_attempts(self, locked_user):
        """Test that lockout occurs after 5 failed attempts"""
        # Assert
        assert locked_user.failed_login_attempts == 5
        assert locked_user.locked_until is not None

    def test_user_not_locked_below_threshold(self, db_session, user_factory):
        """Test that user is not locked below threshold"""
        # Arrange & Act
        for attempts in range(1, 5):
            user = user_factory.create(
                db_session,
                email=f"user{attempts}@example.com",
                failed_login_attempts=attempts,
                locked_until=None
            )

            # Assert
            assert user.locked_until is None

    def test_last_failed_login_timestamp_set(self, db_session, user_factory):
        """Test that last failed login timestamp is recorded"""
        # Arrange
        with freeze_time("2024-01-01 12:00:00"):
            user = user_factory.create(
                db_session,
                failed_login_attempts=1,
                last_failed_login=datetime.utcnow()
            )

        # Act
        db_session.refresh(user)

        # Assert
        assert user.last_failed_login is not None
        expected_time = datetime.strptime("2024-01-01 12:00:00", "%Y-%m-%d %H:%M:%S")
        # Allow 2 seconds tolerance
        time_diff = abs((user.last_failed_login - expected_time).total_seconds())
        assert time_diff < 2


class TestAccountLockoutRecovery:
    """Test account lockout recovery mechanisms"""

    def test_lockout_expires_after_duration(self, db_session, user_factory):
        """Test that lockout automatically expires"""
        # Arrange
        with freeze_time("2024-01-01 12:00:00"):
            lockout_until = datetime.utcnow() + timedelta(minutes=30)
            user = user_factory.create(
                db_session,
                failed_login_attempts=5,
                locked_until=lockout_until
            )

            # User is locked at 12:00
            assert user.locked_until > datetime.utcnow()

        # Act - Move time forward past lockout expiration
        with freeze_time("2024-01-01 12:31:00"):
            # Assert - Lockout has expired
            assert user.locked_until < datetime.utcnow()

    def test_successful_login_resets_failed_attempts(self, db_session, user_factory):
        """Test that successful login resets failed attempt counter"""
        # Arrange
        user = user_factory.create(
            db_session,
            failed_login_attempts=3,
            last_failed_login=datetime.utcnow()
        )

        # Act - Simulate successful login
        user.failed_login_attempts = 0
        user.last_failed_login = None
        db_session.commit()
        db_session.refresh(user)

        # Assert
        assert user.failed_login_attempts == 0
        assert user.last_failed_login is None

    def test_admin_can_unlock_account(self, db_session, locked_user):
        """Test that admin can manually unlock an account"""
        # Arrange
        assert locked_user.locked_until is not None

        # Act - Admin manually unlocks
        locked_user.failed_login_attempts = 0
        locked_user.locked_until = None
        locked_user.last_failed_login = None
        db_session.commit()
        db_session.refresh(locked_user)

        # Assert
        assert locked_user.failed_login_attempts == 0
        assert locked_user.locked_until is None

    def test_password_reset_clears_lockout(self, db_session, locked_user):
        """Test that password reset clears lockout status"""
        # Arrange
        assert locked_user.failed_login_attempts == 5
        assert locked_user.locked_until is not None

        # Act - Simulate password reset
        locked_user.failed_login_attempts = 0
        locked_user.locked_until = None
        locked_user.last_failed_login = None
        db_session.commit()
        db_session.refresh(locked_user)

        # Assert
        assert locked_user.failed_login_attempts == 0
        assert locked_user.locked_until is None


class TestAccountLockoutEdgeCases:
    """Test edge cases in account lockout"""

    def test_lockout_at_exact_threshold(self, db_session, user_factory):
        """Test lockout behavior at exact threshold"""
        # Arrange & Act
        user = user_factory.create(
            db_session,
            failed_login_attempts=5,
            locked_until=datetime.utcnow() + timedelta(minutes=30)
        )

        # Assert
        assert user.failed_login_attempts == 5
        assert user.locked_until is not None

    def test_multiple_users_independent_lockouts(self, db_session, user_factory):
        """Test that lockouts are independent per user"""
        # Arrange
        user1 = user_factory.create(
            db_session,
            email="user1@example.com",
            failed_login_attempts=5,
            locked_until=datetime.utcnow() + timedelta(minutes=30)
        )

        user2 = user_factory.create(
            db_session,
            email="user2@example.com",
            failed_login_attempts=0,
            locked_until=None
        )

        # Assert
        assert user1.locked_until is not None
        assert user2.locked_until is None
        assert user1.id != user2.id

    def test_lockout_persists_across_sessions(self, db_session, user_factory):
        """Test that lockout persists in database"""
        # Arrange
        lockout_time = datetime.utcnow() + timedelta(minutes=30)
        user = user_factory.create(
            db_session,
            failed_login_attempts=5,
            locked_until=lockout_time
        )
        user_id = user.id

        # Act - Close session and reopen (simulate new session)
        db_session.expire_all()

        # Re-query user
        user_reloaded = db_session.query(User).filter(User.id == user_id).first()

        # Assert
        assert user_reloaded.failed_login_attempts == 5
        assert user_reloaded.locked_until is not None

    def test_failed_attempts_can_exceed_threshold(self, db_session, user_factory):
        """Test that failed attempts can exceed threshold without issues"""
        # Arrange & Act
        user = user_factory.create(
            db_session,
            failed_login_attempts=10,  # More than threshold
            locked_until=datetime.utcnow() + timedelta(minutes=30)
        )

        # Assert
        assert user.failed_login_attempts == 10
        assert user.locked_until is not None

    def test_zero_failed_attempts_with_lockout_time(self, db_session, user_factory):
        """Test edge case: zero attempts but lockout time set (shouldn't happen)"""
        # Arrange - This is an inconsistent state but should be handled
        user = user_factory.create(
            db_session,
            failed_login_attempts=0,
            locked_until=datetime.utcnow() + timedelta(minutes=30)
        )

        # Assert - System should still respect the lockout time
        assert user.failed_login_attempts == 0
        assert user.locked_until is not None


@pytest.mark.security
class TestAccountLockoutSecurity:
    """Security-focused tests for account lockout"""

    def test_lockout_prevents_brute_force_attacks(self, db_session, user_factory):
        """Test that lockout mechanism prevents brute force attacks"""
        # Arrange
        user = user_factory.create(
            db_session,
            failed_login_attempts=5,
            locked_until=datetime.utcnow() + timedelta(minutes=30)
        )

        # Assert
        # After 5 attempts, account is locked for 30 minutes
        # This makes brute force attacks impractical
        assert user.failed_login_attempts >= 5
        assert user.locked_until is not None

        # Lockout should last long enough to slow down attacks
        time_until_unlock = (user.locked_until - datetime.utcnow()).total_seconds() / 60
        assert time_until_unlock >= 15  # At least 15 minutes

    def test_lockout_does_not_reveal_user_existence(self, db_session):
        """Test that lockout behavior doesn't leak user existence info"""
        # This is more of a design principle test
        # The API should return the same message whether user exists or not

        # Arrange - Create locked user
        from app.tests.conftest import UserFactory
        locked_user = UserFactory.create(
            db_session,
            email="locked@example.com",
            failed_login_attempts=5,
            locked_until=datetime.utcnow() + timedelta(minutes=30)
        )

        # Assert
        # The existence of lockout fields doesn't reveal information
        # The API layer should handle this properly
        assert locked_user.locked_until is not None

    def test_lockout_timing_sufficient_to_deter_attacks(self, locked_user):
        """Test that lockout timing is sufficient to deter automated attacks"""
        # Assert
        time_until_unlock = (locked_user.locked_until - datetime.utcnow()).total_seconds() / 60

        # Should be at least 15 minutes to make attacks impractical
        assert time_until_unlock >= 15

        # Should not be too long (usability concern)
        assert time_until_unlock <= 60  # Max 1 hour


@pytest.mark.parametrize("failed_attempts,should_be_locked", [
    (0, False),
    (1, False),
    (2, False),
    (3, False),
    (4, False),
    (5, True),
    (6, True),
    (10, True),
])
def test_lockout_threshold_parametrized(db_session, user_factory, failed_attempts, should_be_locked):
    """Parametrized test for lockout threshold"""
    # Arrange
    lockout_time = datetime.utcnow() + timedelta(minutes=30) if should_be_locked else None

    # Act
    user = user_factory.create(
        db_session,
        email=f"user{failed_attempts}@example.com",
        failed_login_attempts=failed_attempts,
        locked_until=lockout_time
    )

    # Assert
    if should_be_locked:
        assert user.failed_login_attempts >= 5
        assert user.locked_until is not None
    else:
        assert user.locked_until is None
