"""Service layer that uses HttpClient for external API calls."""

from http_client import HttpClient


class UserApiService:
    """Fetches user data from the external user API."""

    def __init__(self, client: HttpClient):
        self._client = client

    def get_user(self, user_id: int) -> dict:
        """Fetch a single user by ID."""
        return self._client.get(f"/users/{user_id}")

    def list_users(self, page: int = 1) -> list:
        """Fetch a page of users."""
        data = self._client.get("/users", params={"page": page})
        return data.get("results", [])

    def create_user(self, name: str, email: str) -> dict:
        """Create a new user."""
        return self._client.post("/users", data={"name": name, "email": email})


class NotificationService:
    """Sends notifications via the notification API."""

    def __init__(self, client: HttpClient):
        self._client = client

    def send_email(self, to: str, subject: str, body: str) -> dict:
        """Send an email notification."""
        return self._client.post(
            "/notifications/email",
            data={"to": to, "subject": subject, "body": body},
        )

    def send_webhook(self, url: str, payload: dict) -> dict:
        """Fire a webhook notification."""
        return self._client.post(
            "/notifications/webhook",
            data={"url": url, "payload": payload},
        )
