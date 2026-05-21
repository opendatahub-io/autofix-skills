"""Synchronous HTTP client wrapper."""

import json
from typing import Any


class HttpClient:
    """Simple HTTP client for external API calls."""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = None

    def get(self, path: str, params: dict | None = None) -> dict:
        """Send a GET request.

        Args:
            path: URL path relative to base_url.
            params: Optional query parameters.

        Returns:
            Parsed JSON response.
        """
        import requests
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = requests.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, data: Any = None) -> dict:
        """Send a POST request with JSON body.

        Args:
            path: URL path relative to base_url.
            data: Request body (will be JSON-encoded).

        Returns:
            Parsed JSON response.
        """
        import requests
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = requests.post(
            url,
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()
