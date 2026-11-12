import logging
import os
import sys

BACKEND_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.services.learning_sync_service import (
    process_pending_sync_events,
    process_pending_student_data_sync_events
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():

    logging.info("Starting synchronization worker.")

    try:

        # Skill and proficiency synchronization
        skill_result = process_pending_sync_events(limit=50)

        logging.info(
            "Skill synchronization events processed: %s",
            skill_result["processed"]
        )

        # Profile and project synchronization
        student_data_result = (
            process_pending_student_data_sync_events(limit=20)
        )

        logging.info(
            "Student data synchronization events processed: %s",
            student_data_result["processed"]
        )

        logging.info("Synchronization worker finished.")

    except Exception:

        logging.exception("Synchronization worker failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()