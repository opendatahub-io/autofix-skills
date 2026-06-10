"""Authentication token generation and validation."""

import time
import uuid


class AuthToken:
    """Represents an authentication token."""

    def __init__(self, value: str, username: str, expiration_time: float):
        self.value = value
        self.username = username
        self.expiration_time = expiration_time


class AuthTokenService:
    """Service for generating and validating auth tokens."""

    def __init__(self, token_lifetime_seconds: int):
        self.token_lifetime_seconds = token_lifetime_seconds

    def generate_token(self, username: str) -> AuthToken:
        """Generate a new authentication token.

        Args:
            username: The user to generate a token for.

        Returns:
            A new AuthToken with expiration set.
        """
        token_value = str(uuid.uuid4())
        current_time = time.time_ns()
        expiration_time = current_time + self.token_lifetime_seconds

        return AuthToken(token_value, username, expiration_time)

    def is_token_valid(self, token: AuthToken) -> bool:
        """Check whether a token is still valid.

        Args:
            token: The token to validate.

        Returns:
            True if the token has not expired.
        """
        current_time = time.time()
        return current_time < token.expiration_time
