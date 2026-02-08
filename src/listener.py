"""Subscribe to the commands ntfy topic via Server-Sent Events."""

import json
import logging
import threading

import requests
import sseclient

from src.config import COMMANDS_TOPIC, NTFY_BASE_URL, NTFY_TOKEN
from src.notifier import send_notification
from src.processor import process_greeting

logger = logging.getLogger("hello-app")

BACKOFF_INITIAL = 1
BACKOFF_MAX = 60
BACKOFF_MULTIPLIER = 2


def listen(shutdown_event: "threading.Event | None" = None) -> None:
    """Connect to the SSE stream and process incoming commands.

    Reconnects with exponential backoff on connection failures.
    If shutdown_event is provided, checks it to know when to stop.
    """
    if shutdown_event is None:
        shutdown_event = threading.Event()

    backoff = BACKOFF_INITIAL

    while not shutdown_event.is_set():
        try:
            _connect_and_process(shutdown_event)
            backoff = BACKOFF_INITIAL
        except requests.RequestException as e:
            logger.warning("Connection lost: %s. Reconnecting in %ds...", e, backoff)
            shutdown_event.wait(backoff)
            backoff = min(backoff * BACKOFF_MULTIPLIER, BACKOFF_MAX)
        except Exception as e:
            logger.error("Unexpected error in listener: %s", e)
            shutdown_event.wait(backoff)
            backoff = min(backoff * BACKOFF_MULTIPLIER, BACKOFF_MAX)


def _connect_and_process(shutdown_event: "threading.Event") -> None:
    """Establish SSE connection and handle incoming events."""
    url = f"{NTFY_BASE_URL.rstrip('/')}/{COMMANDS_TOPIC}/sse"

    headers: dict[str, str] = {}
    if NTFY_TOKEN:
        headers["Authorization"] = f"Bearer {NTFY_TOKEN}"

    logger.info("Connecting to SSE stream: %s", url)
    response = requests.get(url, stream=True, headers=headers, timeout=None)
    response.raise_for_status()

    client = sseclient.SSEClient(response)

    for event in client.events():
        if shutdown_event.is_set():
            break

        _handle_event(event)


def _handle_event(event: sseclient.Event) -> None:
    """Process a single SSE event."""
    if event.event != "message":
        logger.debug("Ignoring non-message event: %s", event.event)
        return

    if not event.data or event.data.strip() == "":
        logger.debug("Ignoring empty event")
        return

    try:
        payload = json.loads(event.data)
        message = payload.get("message", "")
    except json.JSONDecodeError:
        message = event.data

    if not message or message.strip() == "":
        logger.debug("Ignoring event with no message content")
        return

    logger.info("Received command: %s", message)

    greeting = process_greeting(message)
    send_notification(greeting)
