"""Tests for registration controller."""

import pytest
from registration_controller import RegistrationController, ValidationError


def test_valid_registration():
    ctrl = RegistrationController()
    result = ctrl.register_user("test@example.com", "password123", "testuser")
    assert result == "User registered successfully"


def test_password_validation_uppercase_required():
    ctrl = RegistrationController()
    with pytest.raises(ValidationError):
        ctrl.register_user("test@example.com", "password123", "testuser")


def test_email_required():
    ctrl = RegistrationController()
    with pytest.raises(ValidationError, match="Email is required"):
        ctrl.register_user(None, "password123", "testuser")


def test_password_required():
    ctrl = RegistrationController()
    with pytest.raises(ValidationError, match="Password is required"):
        ctrl.register_user("test@example.com", None, "testuser")


def test_username_required():
    ctrl = RegistrationController()
    with pytest.raises(ValidationError, match="Username is required"):
        ctrl.register_user("test@example.com", "password123", None)


def test_username_too_short():
    ctrl = RegistrationController()
    with pytest.raises(ValidationError, match="between 3 and 20"):
        ctrl.register_user("test@example.com", "password123", "ab")


def test_username_too_long():
    ctrl = RegistrationController()
    with pytest.raises(ValidationError, match="between 3 and 20"):
        ctrl.register_user("test@example.com", "password123", "thisusernameiswaytoolong")
