"""
Circuit Breaker configuration for external services
Uses pybreaker for resilience against external service failures
"""
import logging
import pybreaker

logger = logging.getLogger(__name__)


class CircuitBreakerListener(pybreaker.CircuitBreakerListener):
    """Custom listener for circuit breaker events"""

    def state_change(self, cb: pybreaker.CircuitBreaker, old_state: str, new_state: str):
        """Log state changes"""
        logger.warning(
            f"Circuit breaker '{cb.name}' state changed: {old_state} -> {new_state}",
            extra={"circuit_breaker": cb.name, "old_state": old_state, "new_state": new_state}
        )

    def failure(self, cb: pybreaker.CircuitBreaker, exc: Exception):
        """Log failures"""
        logger.error(
            f"Circuit breaker '{cb.name}' recorded failure: {type(exc).__name__}: {str(exc)}",
            extra={"circuit_breaker": cb.name, "exception": str(exc)}
        )

    def success(self, cb: pybreaker.CircuitBreaker):
        """Log successes when recovering"""
        if cb.current_state == "half-open":
            logger.info(
                f"Circuit breaker '{cb.name}' success in half-open state",
                extra={"circuit_breaker": cb.name}
            )


# Circuit breaker for Claude API
# Opens after 5 failures, resets after 30 seconds
claude_circuit_breaker = pybreaker.CircuitBreaker(
    name="claude_api",
    fail_max=5,
    reset_timeout=30,
    listeners=[CircuitBreakerListener()],
    exclude=[
        # Don't trip circuit on validation/auth errors
        lambda e: hasattr(e, 'status_code') and e.status_code in (400, 401, 403, 422)
    ]
)

# Circuit breaker for WordPress scanning
# Opens after 3 failures, resets after 60 seconds
wordpress_circuit_breaker = pybreaker.CircuitBreaker(
    name="wordpress_scanner",
    fail_max=3,
    reset_timeout=60,
    listeners=[CircuitBreakerListener()],
    exclude=[
        # Don't trip circuit on client errors
        lambda e: hasattr(e, 'status_code') and 400 <= e.status_code < 500
    ]
)


def get_circuit_breaker_status() -> dict:
    """Get status of all circuit breakers"""
    return {
        "claude_api": {
            "state": claude_circuit_breaker.current_state,
            "fail_counter": claude_circuit_breaker.fail_counter,
            "success_counter": claude_circuit_breaker.success_counter,
        },
        "wordpress_scanner": {
            "state": wordpress_circuit_breaker.current_state,
            "fail_counter": wordpress_circuit_breaker.fail_counter,
            "success_counter": wordpress_circuit_breaker.success_counter,
        }
    }
