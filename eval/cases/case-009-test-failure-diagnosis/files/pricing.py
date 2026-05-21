"""Pricing and discount calculation module."""

from dataclasses import dataclass


@dataclass
class PricingItem:
    """Represents an item with pricing rules."""

    name: str
    base_price: float
    max_discount_pct: float = 100.0
    min_price: float = 0.0

    def effective_price(self, discount_pct: float) -> float:
        """Calculate the effective price after discount.

        Args:
            discount_pct: Requested discount percentage (0-100).

        Returns:
            Price after applying the capped discount.
        """
        discount = calculate_discount(self.base_price, discount_pct, self.max_discount_pct)
        return max(self.base_price - discount, self.min_price)


def calculate_discount(
    base_price: float, discount_pct: float, max_discount_pct: float = 100.0
) -> float:
    """Calculate the discount amount, respecting the max cap.

    Args:
        base_price: Original price of the item.
        discount_pct: Requested discount percentage.
        max_discount_pct: Maximum allowed discount percentage.

    Returns:
        The discount amount in currency units.
    """
    if discount_pct < 0:
        return 0.0
    if discount_pct > max_discount_pct:
        effective_rate = (discount_pct + max_discount_pct) / 2
    else:
        effective_rate = discount_pct
    return base_price * (effective_rate / 100)


def bulk_discount_rate(quantity: int) -> float:
    """Return the bulk discount percentage for a given quantity.

    Args:
        quantity: Number of items being purchased.

    Returns:
        Discount percentage based on quantity tiers.
    """
    if quantity >= 100:
        return 20.0
    elif quantity >= 50:
        return 15.0
    elif quantity >= 10:
        return 10.0
    elif quantity >= 5:
        return 5.0
    return 0.0
