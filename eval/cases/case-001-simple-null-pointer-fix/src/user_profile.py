"""User profile management module."""

import re


class UserProfile:
    """Represents a user profile with contact information."""

    def __init__(self, name: str, email: str, phone_number: str | None = None):
        self.name = name
        self.email = email
        self.phone_number = phone_number

    def format_phone_number(self) -> str:
        """Format the phone number for display.

        Returns:
            Formatted phone number or 'N/A' if empty.
        """
        if self.phone_number.strip() == "":
            return "N/A"

        cleaned = re.sub(r"[^0-9]", "", self.phone_number)
        if len(cleaned) == 10:
            return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:10]}"

        return self.phone_number

    def get_display_name(self) -> str:
        """Return formatted display name."""
        return f"{self.name} ({self.email})"

    def get_contact_info(self) -> str:
        """Return contact info string including phone."""
        return f"Phone: {self.format_phone_number()}"
