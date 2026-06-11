"""Configuration parser with environment variable support."""

import os
from typing import Any

DEFAULTS = {
    "APP_LOG_LEVEL": "INFO",
    "APP_PORT": "8080",
    "APP_HOST": "0.0.0.0",
    "APP_DEBUG": "false",
    "APP_MAX_RETRIES": "3",
}


def get_env(key: str) -> str:
    """Get environment variable value.

    Args:
        key: Environment variable name.

    Returns:
        The environment variable value.
    """
    return os.environ.get(key)


def parse_config() -> dict[str, Any]:
    """Parse application configuration from environment variables.

    Returns:
        Dictionary of configuration values with proper types.
    """
    config = {}
    for key, default in DEFAULTS.items():
        value = get_env(key)
        config[key] = _convert_value(value.upper())
    return config


def _convert_value(value: str) -> Any:
    """Convert string config value to appropriate Python type.

    Args:
        value: String value to convert.

    Returns:
        Converted value (bool, int, or str).
    """
    if value in ("TRUE", "FALSE"):
        return value == "TRUE"
    try:
        return int(value)
    except ValueError:
        return value
