"""Tests for configuration parser."""

import os
from unittest.mock import patch
from config_parser import parse_config, get_env, _convert_value


def test_convert_value_bool_true():
    assert _convert_value("TRUE") is True


def test_convert_value_bool_false():
    assert _convert_value("FALSE") is False


def test_convert_value_int():
    assert _convert_value("8080") == 8080


def test_convert_value_string():
    assert _convert_value("INFO") == "INFO"


def test_get_env_returns_value():
    with patch.dict(os.environ, {"APP_PORT": "9090"}):
        assert get_env("APP_PORT") == "9090"


def test_get_env_returns_none_for_missing():
    result = get_env("NONEXISTENT_VAR_XYZ")
    assert result is None
