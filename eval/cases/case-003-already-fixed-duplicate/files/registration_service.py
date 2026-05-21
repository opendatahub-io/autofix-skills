"""User registration service with input validation."""

import re


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class RegistrationService:
    """Handles user registration with validation."""

    EMAIL_PATTERN = re.compile(
        r"^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )

    def register_user(self, email: str, password: str) -> None:
        """Register a new user after validating inputs.

        Args:
            email: User email address.
            password: User password.

        Raises:
            ValidationError: If email or password is invalid.
        """
        self._validate_email(email)
        print(f"User registered: {email}")

    def _validate_email(self, email: str) -> None:
        if email is None or email.strip() == "":
            raise ValidationError("Email is required")

        if not self.EMAIL_PATTERN.match(email):
            raise ValidationError("Invalid email format")
