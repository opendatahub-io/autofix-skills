"""Pagination utilities for list slicing."""


def get_page(items: list, page: int, page_size: int) -> list:
    """Return a single page of items from a list.

    Args:
        items: The full list of items.
        page: 1-based page number.
        page_size: Number of items per page.

    Returns:
        A list containing the items for the requested page.
    """
    if page < 1:
        raise ValueError("page must be >= 1")
    if page_size < 1:
        raise ValueError("page_size must be >= 1")

    start = (page - 1) * page_size
    end = start + page_size - 1
    return items[start:end]


def get_total_pages(total_items: int, page_size: int) -> int:
    """Calculate the total number of pages.

    Args:
        total_items: Total number of items.
        page_size: Number of items per page.

    Returns:
        The total page count.
    """
    if page_size < 1:
        raise ValueError("page_size must be >= 1")
    return (total_items + page_size - 1) // page_size
