"""
Unit tests for rate limiting functionality
Tests rate limit configuration and client identification
"""
import pytest
from unittest.mock import Mock, MagicMock
from fastapi import Request

from app.core.rate_limiting import (
    get_client_identifier,
    limiter,
    LOGIN_RATE_LIMIT,
    REGISTER_RATE_LIMIT,
    PASSWORD_RESET_RATE_LIMIT,
    API_RATE_LIMIT,
    PUBLIC_RATE_LIMIT
)


class TestGetClientIdentifier:
    """Test client identification for rate limiting"""

    def test_get_client_identifier_with_x_forwarded_for(self):
        """Test that X-Forwarded-For header is used when present"""
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.side_effect = lambda key: {
            "X-Forwarded-For": "192.168.1.100, 10.0.0.1",
            "X-Real-IP": None
        }.get(key)
        mock_request.client.host = "127.0.0.1"

        # Act
        result = get_client_identifier(mock_request)

        # Assert
        assert result == "192.168.1.100"  # Should use first IP

    def test_get_client_identifier_with_x_real_ip(self):
        """Test that X-Real-IP header is used when X-Forwarded-For is absent"""
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.side_effect = lambda key: {
            "X-Forwarded-For": None,
            "X-Real-IP": "203.0.113.50"
        }.get(key)
        mock_request.client.host = "127.0.0.1"

        # Act
        result = get_client_identifier(mock_request)

        # Assert
        assert result == "203.0.113.50"

    def test_get_client_identifier_fallback_to_direct_ip(self):
        """Test fallback to direct client IP when proxy headers absent"""
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = None
        mock_request.client.host = "198.51.100.75"

        # Act - Need to mock get_remote_address since it's imported
        with pytest.mock.patch('app.core.rate_limiting.get_remote_address') as mock_get_remote:
            mock_get_remote.return_value = "198.51.100.75"
            result = get_client_identifier(mock_request)

        # Assert
        assert result == "198.51.100.75"

    def test_get_client_identifier_strips_whitespace(self):
        """Test that whitespace is stripped from IP addresses"""
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.side_effect = lambda key: {
            "X-Forwarded-For": "  192.168.1.100  , 10.0.0.1",
            "X-Real-IP": None
        }.get(key)

        # Act
        result = get_client_identifier(mock_request)

        # Assert
        assert result == "192.168.1.100"
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    def test_get_client_identifier_handles_multiple_forwarded_ips(self):
        """Test that first IP is used when multiple IPs in X-Forwarded-For"""
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.side_effect = lambda key: {
            "X-Forwarded-For": "192.168.1.1, 10.0.0.1, 172.16.0.1",
            "X-Real-IP": None
        }.get(key)

        # Act
        result = get_client_identifier(mock_request)

        # Assert
        assert result == "192.168.1.1"

    def test_get_client_identifier_priority_order(self):
        """Test that X-Forwarded-For has priority over X-Real-IP"""
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.side_effect = lambda key: {
            "X-Forwarded-For": "192.168.1.100",
            "X-Real-IP": "203.0.113.50"
        }.get(key)

        # Act
        result = get_client_identifier(mock_request)

        # Assert
        assert result == "192.168.1.100"  # X-Forwarded-For takes priority


class TestRateLimiterConfiguration:
    """Test rate limiter configuration"""

    def test_limiter_initialized(self):
        """Test that limiter is properly initialized"""
        # Assert
        assert limiter is not None
        assert hasattr(limiter, 'key_func')

    def test_limiter_uses_custom_key_function(self):
        """Test that limiter uses get_client_identifier as key function"""
        # Assert
        assert limiter._key_func == get_client_identifier

    def test_limiter_headers_enabled(self):
        """Test that rate limit headers are enabled"""
        # Assert
        assert limiter._headers_enabled is True

    def test_limiter_has_no_default_limits(self):
        """Test that no default limits are set (we apply per-endpoint)"""
        # Assert
        assert limiter._default_limits == []


class TestRateLimitConstants:
    """Test rate limit constant values"""

    def test_login_rate_limit_is_defined(self):
        """Test that login rate limit is properly configured"""
        # Assert
        assert LOGIN_RATE_LIMIT is not None
        assert isinstance(LOGIN_RATE_LIMIT, str)
        assert "/" in LOGIN_RATE_LIMIT  # Format: "X/time"

    def test_login_rate_limit_is_reasonable(self):
        """Test that login rate limit allows legitimate attempts"""
        # Assert
        # Should allow at least 5 attempts
        assert LOGIN_RATE_LIMIT == "5/15minutes"

    def test_register_rate_limit_is_defined(self):
        """Test that registration rate limit is properly configured"""
        # Assert
        assert REGISTER_RATE_LIMIT is not None
        assert isinstance(REGISTER_RATE_LIMIT, str)
        assert "/" in REGISTER_RATE_LIMIT

    def test_register_rate_limit_is_stricter_than_login(self):
        """Test that registration is more strictly rate limited"""
        # Assert
        # Registration should be stricter to prevent spam
        assert REGISTER_RATE_LIMIT == "3/hour"

    def test_password_reset_rate_limit_is_defined(self):
        """Test that password reset rate limit is properly configured"""
        # Assert
        assert PASSWORD_RESET_RATE_LIMIT is not None
        assert isinstance(PASSWORD_RESET_RATE_LIMIT, str)

    def test_password_reset_rate_limit_is_strict(self):
        """Test that password reset has strict rate limit"""
        # Assert
        assert PASSWORD_RESET_RATE_LIMIT == "3/hour"

    def test_api_rate_limit_is_defined(self):
        """Test that general API rate limit is defined"""
        # Assert
        assert API_RATE_LIMIT is not None
        assert API_RATE_LIMIT == "60/minute"

    def test_public_rate_limit_is_defined(self):
        """Test that public endpoint rate limit is defined"""
        # Assert
        assert PUBLIC_RATE_LIMIT is not None
        assert PUBLIC_RATE_LIMIT == "100/minute"

    def test_public_rate_limit_is_more_permissive_than_api(self):
        """Test that public endpoints have more permissive limits"""
        # Assert
        # Extract numbers from rate limit strings
        api_limit = int(API_RATE_LIMIT.split("/")[0])
        public_limit = int(PUBLIC_RATE_LIMIT.split("/")[0])

        assert public_limit > api_limit


class TestRateLimitFormats:
    """Test rate limit format validity"""

    @pytest.mark.parametrize("rate_limit", [
        LOGIN_RATE_LIMIT,
        REGISTER_RATE_LIMIT,
        PASSWORD_RESET_RATE_LIMIT,
        API_RATE_LIMIT,
        PUBLIC_RATE_LIMIT
    ])
    def test_rate_limit_format_is_valid(self, rate_limit):
        """Test that all rate limits follow valid format"""
        # Assert
        parts = rate_limit.split("/")
        assert len(parts) == 2, f"Rate limit {rate_limit} should have format 'X/time'"

        # First part should be a number
        count = parts[0]
        assert count.isdigit(), f"Rate count {count} should be numeric"

        # Second part should be a time unit
        time_unit = parts[1]
        valid_units = ["second", "seconds", "minute", "minutes", "hour", "hours", "day", "days"]
        # May have number prefix like "15minutes"
        has_valid_unit = any(unit in time_unit for unit in valid_units)
        assert has_valid_unit, f"Time unit {time_unit} should be valid"


class TestRateLimitIntegration:
    """Integration tests for rate limiting with FastAPI"""

    def test_rate_limiter_can_be_applied_to_endpoint(self, client):
        """Test that rate limiter can decorate an endpoint"""
        # This is more of a smoke test to ensure the limiter works with FastAPI
        # Arrange - the client fixture already has the app with rate limiting

        # Act - Make a request to a public endpoint
        response = client.get("/")

        # Assert - Should work without rate limit errors
        assert response.status_code in [200, 404]  # Either works or endpoint doesn't exist

    def test_rate_limit_storage_is_configured(self):
        """Test that rate limit storage backend is configured"""
        # Assert
        assert hasattr(limiter, '_storage')
        # In test mode, we use memory storage
        assert limiter._storage_uri == "memory://"


class TestClientIdentificationEdgeCases:
    """Test edge cases in client identification"""

    def test_get_client_identifier_with_empty_forwarded_for(self):
        """Test handling of empty X-Forwarded-For header"""
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.side_effect = lambda key: {
            "X-Forwarded-For": "",
            "X-Real-IP": "203.0.113.50"
        }.get(key)

        # Act
        result = get_client_identifier(mock_request)

        # Assert - Should fall back to X-Real-IP
        assert result == "203.0.113.50"

    def test_get_client_identifier_with_ipv6(self):
        """Test handling of IPv6 addresses"""
        # Arrange
        mock_request = Mock(spec=Request)
        ipv6_address = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        mock_request.headers.get.side_effect = lambda key: {
            "X-Forwarded-For": ipv6_address,
            "X-Real-IP": None
        }.get(key)

        # Act
        result = get_client_identifier(mock_request)

        # Assert
        assert result == ipv6_address

    def test_get_client_identifier_with_localhost(self):
        """Test handling of localhost addresses"""
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.side_effect = lambda key: {
            "X-Forwarded-For": "127.0.0.1",
            "X-Real-IP": None
        }.get(key)

        # Act
        result = get_client_identifier(mock_request)

        # Assert
        assert result == "127.0.0.1"


@pytest.mark.security
class TestRateLimitSecurity:
    """Security-focused rate limiting tests"""

    def test_rate_limits_prevent_brute_force_login(self):
        """Test that login rate limits can prevent brute force attacks"""
        # Assert
        # Parse login rate limit
        attempts, period = LOGIN_RATE_LIMIT.split("/")
        attempts = int(attempts)

        # Should allow reasonable legitimate attempts (3-10)
        assert 3 <= attempts <= 10, "Login rate limit should allow 3-10 attempts"

        # Should have a reasonable time window (minutes or hours, not seconds)
        assert "minute" in period or "hour" in period, \
            "Login rate limit window should be in minutes or hours"

    def test_rate_limits_prevent_account_enumeration(self):
        """Test that registration rate limits prevent account enumeration"""
        # Assert
        attempts, period = REGISTER_RATE_LIMIT.split("/")
        attempts = int(attempts)

        # Should be very restrictive for registration
        assert attempts <= 5, "Registration should allow few attempts"
        assert "hour" in period, "Registration rate limit should be per hour"

    def test_rate_limits_prevent_password_reset_abuse(self):
        """Test that password reset rate limits prevent abuse"""
        # Assert
        attempts, period = PASSWORD_RESET_RATE_LIMIT.split("/")
        attempts = int(attempts)

        # Should be strict for password reset
        assert attempts <= 5, "Password reset should be strictly limited"
        assert "hour" in period or "day" in period, \
            "Password reset should have long time window"
