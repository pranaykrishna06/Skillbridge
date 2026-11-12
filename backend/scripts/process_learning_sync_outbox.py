import logging
import os
import sys

BACKEND_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.services.learning_sync_service import (
    process_pending_sync_events
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():

    logging.info("Starting learning synchronization worker.")

    try:
        result = process_pending_sync_events(limit=50)

        logging.info(
            "Synchronization worker finished. Processed: %s",
            result["processed"]
        )

        for event in result["results"]:
            logging.info("Event result: %s", event)

    except Exception:
        logging.exception("Learning synchronization worker failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()