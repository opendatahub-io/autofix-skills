"""Tests for pricing module."""

from pricing import PricingItem, calculate_discount, bulk_discount_rate


def test_calculate_discount_no_cap():
    result = calculate_discount(100.0, 10.0)
    assert result == 10.0


def test_calculate_discount_percentage():
    """Discount should be capped at max_discount_pct when request exceeds it."""
    result = calculate_discount(100.0, 25.0, max_discount_pct=15.0)
    assert result == 15.0


def test_calculate_discount_negative():
    result = calculate_discount(100.0, -5.0)
    assert result == 0.0


def test_calculate_discount_at_cap():
    result = calculate_discount(200.0, 15.0, max_discount_pct=15.0)
    assert result == 30.0


def test_effective_price_basic():
    item = PricingItem("Widget", base_price=50.0)
    assert item.effective_price(10.0) == 45.0


def test_effective_price_with_cap():
    item = PricingItem("Widget", base_price=100.0, max_discount_pct=10.0)
    assert item.effective_price(50.0) == 90.0


def test_effective_price_respects_min():
    item = PricingItem("Widget", base_price=10.0, min_price=5.0)
    assert item.effective_price(80.0) == 5.0


def test_bulk_discount_rate_tiers():
    assert bulk_discount_rate(1) == 0.0
    assert bulk_discount_rate(5) == 5.0
    assert bulk_discount_rate(10) == 10.0
    assert bulk_discount_rate(50) == 15.0
    assert bulk_discount_rate(100) == 20.0
