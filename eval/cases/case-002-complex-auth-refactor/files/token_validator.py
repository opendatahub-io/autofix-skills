"""Token validation and session management."""

from auth_token_service import AuthToken, AuthTokenService


class TokenValidator:
    """Validates and manages active tokens."""

    def __init__(self, token_service: AuthTokenService):
        self.token_service = token_service
        self._active_tokens: dict[str, AuthToken] = {}

    def register_token(self, token: AuthToken) -> None:
        """Register a newly issued token."""
        self._active_tokens[token.value] = token

    def validate_token(self, token_value: str) -> bool:
        """Check if a token is valid and active.

        Args:
            token_value: The token string to validate.

        Returns:
            True if the token exists and has not expired.
        """
        token = self._active_tokens.get(token_value)
        if token is None:
            return False

        if not self.token_service.is_token_valid(token):
            del self._active_tokens[token_value]
            return False

        return True

    def invalidate_token(self, token_value: str) -> None:
        """Remove a token from the active set."""
        self._active_tokens.pop(token_value, None)

    def get_username_for_token(self, token_value: str) -> str | None:
        """Look up the username associated with a token."""
        token = self._active_tokens.get(token_value)
        return token.username if token else None
