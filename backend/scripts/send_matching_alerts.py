import os
import sys
from datetime import datetime

# Add backend directory to Python path.
BACKEND_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, BACKEND_DIR)

from app.services.matching_alert_service import (
    generate_matching_internship_alerts
)


# ==========================================
# MATCHING ALERT JOB
# ==========================================

def main():

    print("=" * 55)
    print("SKILLBRIDGE MATCHING INTERNSHIP ALERT SERVICE")
    print("=" * 55)

    print("Execution time:", datetime.now())

    try:

        result = generate_matching_internship_alerts()

        print("\nExecution completed successfully.")

        print(
            "Students processed:",
            result["students_processed"]
        )

        print(
            "Matching internships found:",
            result["matching_internships_found"]
        )

        print(
            "Notifications created:",
            result["notifications_created"]
        )

        print("\nStatus: SUCCESS")

    except Exception as error:

        print("\nStatus: FAILED")
        print("Error:", str(error))

        sys.exit(1)


if __name__ == "__main__":
    main()