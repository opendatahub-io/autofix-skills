"""User registration controller with input validation."""

import re


class ValidationError(Exception):
    """Raised when input validation fails."""

    pass


class RegistrationController:
    """Handles user registration with input validation."""

    PASSWORD_PATTERN = re.compile(r"[a-z0-9]{8,}")
    USERNAME_PATTERN = re.compile(r"[a-zA-Z0-9]{3,20}")

    def register_user(self, email: str, password: str, username: str) -> str:
        """Register a new user after validating all inputs.

        Args:
            email: User email address.
            password: User password.
            username: Desired username.

        Returns:
            Success message string.

        Raises:
            ValidationError: If any input is invalid.
        """
        self._validate_email(email)
        self._validate_password(password)
        self._validate_username(username)

        return "User registered successfully"

    def _validate_email(self, email: str) -> None:
        if email is None or email.strip() == "":
            raise ValidationError("Email is required")

        if "@" not in email:
            raise ValidationError(f"Invalid email format: {self.PASSWORD_PATTERN.pattern}")

    def _validate_password(self, password: str) -> None:
        if password is None or password.strip() == "":
            raise ValidationError("Password is required")

        if not self.PASSWORD_PATTERN.match(password):
            raise ValidationError(f"Invalid password format: {self.PASSWORD_PATTERN.pattern}")

    def _validate_username(self, username: str) -> None:
        if username is None or username.strip() == "":
            raise ValidationError("Username is required")

        if len(username) < 3 or len(username) > 20:
            raise ValidationError("Username must be between 3 and 20 characters")
