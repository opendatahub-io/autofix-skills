"""Tests for API service layer."""

from unittest.mock import MagicMock

from api_service import NotificationService, UserApiService


def test_get_user_calls_client():
    client = MagicMock()
    client.get.return_value = {"id": 1, "name": "Alice"}
    svc = UserApiService(client)
    result = svc.get_user(1)
    client.get.assert_called_once_with("/users/1")
    assert result["name"] == "Alice"


def test_list_users_passes_page_param():
    client = MagicMock()
    client.get.return_value = {"results": [{"id": 1}]}
    svc = UserApiService(client)
    result = svc.list_users(page=2)
    client.get.assert_called_once_with("/users", params={"page": 2})
    assert len(result) == 1


def test_send_email_posts_notification():
    client = MagicMock()
    client.post.return_value = {"status": "sent"}
    svc = NotificationService(client)
    result = svc.send_email("a@b.com", "Hi", "Hello")
    client.post.assert_called_once()
    assert result["status"] == "sent"
