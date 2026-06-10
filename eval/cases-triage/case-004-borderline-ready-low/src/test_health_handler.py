"""Tests for health check handler."""

from health_handler import HealthChecker


def test_initial_health_check_returns_ok():
    checker = HealthChecker(check_interval=30)
    status, body = checker.handle_request()
    assert status == 200
    assert body["status"] == "ok"


def test_cached_check_returns_previous_result():
    checker = HealthChecker(check_interval=60)
    checker.handle_request()
    status, body = checker.handle_request()
    assert status == 200


def test_unhealthy_when_db_fails(monkeypatch):
    checker = HealthChecker(check_interval=0)
    monkeypatch.setattr(
        checker, "_check_database", lambda: (_ for _ in ()).throw(ConnectionError("db down"))
    )
    status, body = checker.handle_request()
    assert status == 503
    assert body["status"] == "unhealthy"
