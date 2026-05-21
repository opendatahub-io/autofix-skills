"""Tests for registration service."""

import pytest

from registration_service import RegistrationService, ValidationError


def test_valid_email_succeeds():
    svc = RegistrationService()
    svc.register_user("test@example.com", "password123")


def test_invalid_email_format_raises_error():
    svc = RegistrationService()
    with pytest.raises(ValidationError, match="Invalid email format"):
        svc.register_user("notanemail", "password123")


def test_none_email_raises_error():
    svc = RegistrationService()
    with pytest.raises(ValidationError, match="Email is required"):
        svc.register_user(None, "password123")


def test_empty_email_raises_error():
    svc = RegistrationService()
    with pytest.raises(ValidationError, match="Email is required"):
        svc.register_user("", "password123")
