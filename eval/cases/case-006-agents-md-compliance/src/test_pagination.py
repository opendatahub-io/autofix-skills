"""Tests for pagination utilities."""

import pytest
from pagination import get_page, get_total_pages


def test_get_page_first_page_returns_correct_items():
    items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    result = get_page(items, page=1, page_size=3)
    assert result == [1, 2, 3]


def test_get_page_middle_page_returns_correct_items():
    items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    result = get_page(items, page=2, page_size=3)
    assert result == [4, 5, 6]


def test_get_page_invalid_page_raises_error():
    with pytest.raises(ValueError):
        get_page([1, 2, 3], page=0, page_size=2)


def test_get_page_invalid_page_size_raises_error():
    with pytest.raises(ValueError):
        get_page([1, 2, 3], page=1, page_size=0)


def test_get_total_pages_exact_division_returns_correct_count():
    assert get_total_pages(10, 5) == 2


def test_get_total_pages_remainder_returns_extra_page():
    assert get_total_pages(11, 5) == 3
