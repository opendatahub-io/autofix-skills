"""Tests for authentication token service."""

import time

from auth_token_service import AuthTokenService


def test_generate_token_returns_token():
    service = AuthTokenService(86400)
    token = service.generate_token("testuser")

    assert token is not None
    assert token.username == "testuser"
    assert token.value is not None
    assert token.expiration_time > time.time()


def test_is_token_valid_for_fresh_token():
    service = AuthTokenService(86400)
    token = service.generate_token("testuser")

    assert service.is_token_valid(token) is True


def test_token_expiration():
    service = AuthTokenService(1)
    token = service.generate_token("testuser")

    time.sleep(2)

    assert service.is_token_valid(token) is False


def test_token_lifetime_is_correct():
    expected_lifetime = 86400
    service = AuthTokenService(expected_lifetime)
    token = service.generate_token("testuser")

    current_time = time.time()
    token_lifetime = token.expiration_time - current_time

    assert abs(token_lifetime - expected_lifetime) < 2, (
        f"Token lifetime should be ~{expected_lifetime}s, got {token_lifetime:.1f}s"
    )
