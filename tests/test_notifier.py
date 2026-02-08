"""Tests for ntfy notifier."""

from unittest.mock import patch, MagicMock

import requests

from src.notifier import send_notification


@patch("src.notifier.requests.post")
def test_send_notification_success(mock_post):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    result = send_notification("Hello World!")

    assert result is True
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert call_kwargs.kwargs["data"] == b"Hello World!"
    assert "Title" in call_kwargs.kwargs["headers"]


@patch("src.notifier.requests.post")
def test_send_notification_failure(mock_post):
    mock_post.side_effect = requests.RequestException("Connection error")

    result = send_notification("Hello World!")

    assert result is False


@patch("src.notifier.NTFY_TOKEN", "tk_test123")
@patch("src.notifier.requests.post")
def test_send_notification_with_auth_token(mock_post):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    send_notification("Hello World!")

    call_kwargs = mock_post.call_args
    assert call_kwargs.kwargs["headers"]["Authorization"] == "Bearer tk_test123"


@patch("src.notifier.NTFY_TOKEN", "")
@patch("src.notifier.requests.post")
def test_send_notification_without_auth_token(mock_post):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    send_notification("Hello World!")

    call_kwargs = mock_post.call_args
    assert "Authorization" not in call_kwargs.kwargs["headers"]
