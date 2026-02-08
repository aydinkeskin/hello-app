"""Tests for SSE listener."""

from unittest.mock import patch, MagicMock

from src.listener import _handle_event


@patch("src.listener.send_notification")
@patch("src.listener.process_greeting", return_value="Hello World!")
def test_handle_event_valid(mock_process, mock_notify):
    event = MagicMock()
    event.data = "World"

    _handle_event(event)

    mock_process.assert_called_once_with("World")
    mock_notify.assert_called_once_with("Hello World!")


@patch("src.listener.send_notification")
@patch("src.listener.process_greeting")
def test_handle_event_empty(mock_process, mock_notify):
    event = MagicMock()
    event.data = ""

    _handle_event(event)

    mock_process.assert_not_called()
    mock_notify.assert_not_called()


@patch("src.listener.send_notification")
@patch("src.listener.process_greeting")
def test_handle_event_whitespace_only(mock_process, mock_notify):
    event = MagicMock()
    event.data = "   "

    _handle_event(event)

    mock_process.assert_not_called()
    mock_notify.assert_not_called()


@patch("src.listener.send_notification")
@patch("src.listener.process_greeting")
def test_handle_event_none_data(mock_process, mock_notify):
    event = MagicMock()
    event.data = None

    _handle_event(event)

    mock_process.assert_not_called()
    mock_notify.assert_not_called()
