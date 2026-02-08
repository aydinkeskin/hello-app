"""Publish greeting results to ntfy."""

import logging

import requests

from src.config import NTFY_BASE_URL, NTFY_TOKEN, RESULTS_TOPIC

logger = logging.getLogger("hello-app")

PUBLISH_TIMEOUT = 10


def send_notification(greeting: str) -> bool:
    """Publish a greeting to the results ntfy topic.

    Returns True on success, False on failure. Fire-and-forget for MVP.
    """
    url = f"{NTFY_BASE_URL.rstrip('/')}/{RESULTS_TOPIC}"

    headers: dict[str, str] = {
        "Title": "Hello App \U0001f44b".encode("utf-8").decode("latin-1"),
        "Priority": "default",
    }
    if NTFY_TOKEN:
        headers["Authorization"] = f"Bearer {NTFY_TOKEN}"

    try:
        response = requests.post(
            url, data=greeting.encode("utf-8"), headers=headers, timeout=PUBLISH_TIMEOUT
        )
        response.raise_for_status()
        logger.info("Notification sent: %s", greeting)
        return True
    except requests.RequestException as e:
        logger.error("Failed to send notification: %s", e)
        return False
