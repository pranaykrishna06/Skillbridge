import sys
from pathlib import Path

# Add backend directory to Python path
BACKEND_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(BACKEND_DIR))


from app.services.embedding_update_service import (
    synchronize_all_embeddings
)


def main():

    print("=" * 60)
    print("SKILLBRIDGE EMBEDDING SYNCHRONIZATION")
    print("=" * 60)

    print("\nStarting embedding synchronization...\n")

    result = synchronize_all_embeddings()

    print("\nSTUDENT EMBEDDINGS")
    print("-" * 40)

    students = result["students"]

    print("Total:", students["total"])
    print("Successful:", students["successful"])
    print("Failed:", students["failed"])

    print("\nINTERNSHIP EMBEDDINGS")
    print("-" * 40)

    internships = result["internships"]

    print("Total:", internships["total"])
    print("Successful:", internships["successful"])
    print("Failed:", internships["failed"])

    print("\nFINAL STATUS")
    print("-" * 40)

    print(result["status"])

    if students["errors"] or internships["errors"]:

        print("\nERROR DETAILS:")

        for error in students["errors"]:
            print(error)

        for error in internships["errors"]:
            print(error)

    print("\nEmbedding synchronization completed.")

    print("=" * 60)


if __name__ == "__main__":
    main()
