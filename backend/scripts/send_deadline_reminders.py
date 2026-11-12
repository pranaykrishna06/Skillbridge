import os
import sys
from datetime import datetime

# Add backend directory to Python path
BACKEND_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, BACKEND_DIR)

from app.services.deadline_reminder_service import (
    send_deadline_reminders
)


# ==========================================
# DAILY DEADLINE REMINDER JOB
# ==========================================

def main():

    print("=" * 50)
    print("SKILLBRIDGE DEADLINE REMINDER SERVICE")
    print("=" * 50)

    print("Execution time:", datetime.now())

    try:

        result = send_deadline_reminders()

        print("\nReminder execution completed.")

        print(
            "Three-day reminders:",
            result["three_day_reminders"]
        )

        print(
            "One-day reminders:",
            result["one_day_reminders"]
        )

        print(
            "Total reminders created:",
            result["reminders_created"]
        )

        print("\nStatus: SUCCESS")

    except Exception as error:

        print("\nStatus: FAILED")
        print("Error:", str(error))

        sys.exit(1)


if __name__ == "__main__":
    main()