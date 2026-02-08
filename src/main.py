"""Entry point — starts the listener and handles graceful shutdown."""

import signal
import threading
import time

from src.config import COMMANDS_TOPIC, setup_logging, validate_config
from src.listener import listen


def main() -> None:
    """Start the hello-app service."""
    validate_config()
    logger = setup_logging()

    shutdown_event = threading.Event()
    start_time = time.monotonic()

    def handle_signal(signum: int, frame: object) -> None:
        logger.info("Received signal %s, shutting down...", signal.Signals(signum).name)
        shutdown_event.set()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    logger.info("Listening on %s...", COMMANDS_TOPIC)

    # Health logging in a background thread
    def health_log() -> None:
        while not shutdown_event.is_set():
            shutdown_event.wait(300)  # 5 minutes
            if not shutdown_event.is_set():
                elapsed = time.monotonic() - start_time
                hours = int(elapsed // 3600)
                minutes = int((elapsed % 3600) // 60)
                logger.info("Still listening... (uptime: %dh %dm)", hours, minutes)

    health_thread = threading.Thread(target=health_log, daemon=True)
    health_thread.start()

    listen(shutdown_event)

    logger.info("Service stopped")


if __name__ == "__main__":
    main()
