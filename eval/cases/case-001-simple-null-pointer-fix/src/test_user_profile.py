"""Tests for user profile module."""

from user_profile import UserProfile


def test_format_phone_number_with_valid_number():
    profile = UserProfile("John Doe", "john@example.com", "5551234567")
    assert profile.format_phone_number() == "(555) 123-4567"


def test_format_phone_number_with_dashes():
    profile = UserProfile("Jane Smith", "jane@example.com", "555-123-4567")
    assert profile.format_phone_number() == "(555) 123-4567"


def test_format_phone_number_with_parentheses():
    profile = UserProfile("Bob Jones", "bob@example.com", "(555) 123-4567")
    assert profile.format_phone_number() == "(555) 123-4567"


def test_format_phone_number_with_empty_string():
    profile = UserProfile("Alice Brown", "alice@example.com", "")
    assert profile.format_phone_number() == "N/A"


def test_get_display_name():
    profile = UserProfile("Test User", "test@example.com", "5551234567")
    assert profile.get_display_name() == "Test User (test@example.com)"
