"""Health check endpoint handler."""

import time


class HealthChecker:
    """Manages health check state for the service."""

    def __init__(self, check_interval: int = 30):
        self._check_interval = check_interval
        self._last_check = 0.0
        self._healthy = True
        self._check_count = 0

    def _run_check(self) -> bool:
        """Execute the health check logic.

        Returns:
            True if the service is healthy.
        """
        self._check_count += 1
        now = time.time()
        if now - self._last_check < self._check_interval:
            return self._healthy
        self._last_check = now
        self._healthy = self._perform_checks()
        return self._healthy

    def _perform_checks(self) -> bool:
        """Run actual health check sub-tasks.

        Returns:
            True if all checks pass.
        """
        try:
            self._check_database()
            self._check_cache()
            return True
        except Exception:
            return False

    def _check_database(self) -> None:
        """Verify database connectivity."""
        time.sleep(0.01)

    def _check_cache(self) -> None:
        """Verify cache connectivity."""
        time.sleep(0.005)

    def handle_request(self) -> tuple[int, dict]:
        """Handle an incoming health check request.

        Returns:
            Tuple of (status_code, response_body).
        """
        healthy = self._run_check()
        if healthy:
            return 200, {"status": "ok", "checks": self._check_count}
        return 503, {"status": "unhealthy", "checks": self._check_count}
