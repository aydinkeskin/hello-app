"""Load and validate configuration from environment variables."""

import logging
import sys

from dotenv import load_dotenv
import os


load_dotenv()

COMMANDS_TOPIC: str = os.getenv("COMMANDS_TOPIC", "")
RESULTS_TOPIC: str = os.getenv("RESULTS_TOPIC", "")
NTFY_BASE_URL: str = os.getenv("NTFY_BASE_URL", "https://ntfy.sh")
NTFY_TOKEN: str = os.getenv("NTFY_TOKEN", "")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


def validate_config() -> None:
    """Validate that required configuration is present."""
    missing = []
    if not COMMANDS_TOPIC:
        missing.append("COMMANDS_TOPIC")
    if not RESULTS_TOPIC:
        missing.append("RESULTS_TOPIC")

    if missing:
        print(
            f"Missing required environment variables: {', '.join(missing)}",
            file=sys.stderr,
        )
        print(
            "Copy .env.example to .env and fill in your topic names.", file=sys.stderr
        )
        sys.exit(1)


def setup_logging() -> logging.Logger:
    """Configure and return the application logger."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("hello-app")
