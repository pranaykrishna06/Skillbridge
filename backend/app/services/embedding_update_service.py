from app.db.postgres import get_postgres_connection


# ============================================================
# 1. SAFE STUDENT EMBEDDING UPDATE
# ============================================================

def refresh_student_embedding(student_id):
    """
    Refresh a student's semantic embedding.

    Failures are logged without affecting the original
    PostgreSQL profile, skill, or project operation.
    """

    try:
        from app.services.embedding_db_service import (
            generate_student_embedding
        )

        result = generate_student_embedding(student_id)

        print(
            f"Student embedding successfully refreshed: {student_id}"
        )

        return {
            "status": "success",
            "student_id": student_id,
            "result": result
        }

    except Exception as error:

        print(
            f"Student embedding refresh failed "
            f"for {student_id}: {error}"
        )

        return {
            "status": "failed",
            "student_id": student_id,
            "error": str(error)
        }


# ============================================================
# 2. SAFE INTERNSHIP EMBEDDING UPDATE
# ============================================================

def refresh_internship_embedding(internship_id):
    """
    Refresh an internship's semantic embedding.

    Failures do not undo the original internship operation.
    """

    try:
        from app.services.embedding_db_service import (
            generate_internship_embedding
        )

        result = generate_internship_embedding(internship_id)

        print(
            f"Internship embedding successfully refreshed: "
            f"{internship_id}"
        )

        return {
            "status": "success",
            "internship_id": internship_id,
            "result": result
        }

    except Exception as error:

        print(
            f"Internship embedding refresh failed "
            f"for {internship_id}: {error}"
        )

        return {
            "status": "failed",
            "internship_id": internship_id,
            "error": str(error)
        }


# ============================================================
# 3. RETRIEVE ALL STUDENT IDS
# ============================================================

def get_all_student_ids():

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT student_id
                FROM students
                ORDER BY student_id
            """)

            return [
                row[0]
                for row in cursor.fetchall()
            ]

    finally:
        connection.close()


# ============================================================
# 4. RETRIEVE ALL INTERNSHIP IDS
# ============================================================

def get_all_internship_ids():

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT internship_id
                FROM internships
                ORDER BY internship_id
            """)

            return [
                row[0]
                for row in cursor.fetchall()
            ]

    finally:
        connection.close()


# ============================================================
# 5. FIND MISSING OR OUTDATED EMBEDDINGS
# ============================================================

def get_embedding_sync_status():

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    s.student_id,
                    CASE
                        WHEN e.student_id IS NULL
                        THEN 'missing'
                        WHEN e.source_text IS NULL
                        THEN 'missing_source'
                        ELSE 'present'
                    END AS embedding_status
                FROM students s
                LEFT JOIN student_embeddings e
                    ON s.student_id = e.student_id
                ORDER BY s.student_id
            """)

            student_status = cursor.fetchall()

            cursor.execute("""
                SELECT
                    i.internship_id,
                    CASE
                        WHEN e.internship_id IS NULL
                        THEN 'missing'
                        WHEN e.source_text IS NULL
                        THEN 'missing_source'
                        ELSE 'present'
                    END AS embedding_status
                FROM internships i
                LEFT JOIN internship_embeddings e
                    ON i.internship_id = e.internship_id
                ORDER BY i.internship_id
            """)

            internship_status = cursor.fetchall()

        return {
            "students": [
                {
                    "id": row[0],
                    "status": row[1]
                }
                for row in student_status
            ],
            "internships": [
                {
                    "id": row[0],
                    "status": row[1]
                }
                for row in internship_status
            ]
        }

    finally:
        connection.close()


# ============================================================
# 6. SYNCHRONIZE ALL STUDENT EMBEDDINGS
# ============================================================

def synchronize_student_embeddings():
    """
    Regenerate embeddings for all existing students.

    Individual failures do not stop the remaining records.
    """

    student_ids = get_all_student_ids()

    successful = 0
    failed = 0
    errors = []

    for student_id in student_ids:

        result = refresh_student_embedding(student_id)

        if result["status"] == "success":

            successful += 1

        else:

            failed += 1

            errors.append({
                "student_id": student_id,
                "error": result["error"]
            })

    return {
        "total": len(student_ids),
        "successful": successful,
        "failed": failed,
        "errors": errors
    }


# ============================================================
# 7. SYNCHRONIZE ALL INTERNSHIP EMBEDDINGS
# ============================================================

def synchronize_internship_embeddings():
    """
    Regenerate embeddings for all existing internships.

    Individual failures do not stop the remaining records.
    """

    internship_ids = get_all_internship_ids()

    successful = 0
    failed = 0
    errors = []

    for internship_id in internship_ids:

        result = refresh_internship_embedding(internship_id)

        if result["status"] == "success":

            successful += 1

        else:

            failed += 1

            errors.append({
                "internship_id": internship_id,
                "error": result["error"]
            })

    return {
        "total": len(internship_ids),
        "successful": successful,
        "failed": failed,
        "errors": errors
    }


# ============================================================
# 8. COMPLETE EMBEDDING SYNCHRONIZATION
# ============================================================

def synchronize_all_embeddings():
    """
    Regenerate student and internship embeddings.

    This can be used for initial setup, model changes,
    and recovery of missing or outdated embeddings.
    """

    student_results = synchronize_student_embeddings()

    internship_results = synchronize_internship_embeddings()

    return {
        "status": (
            "success"
            if (
                student_results["failed"] == 0
                and internship_results["failed"] == 0
            )
            else "partial_success"
        ),

        "message": "Embedding synchronization completed.",

        "students": student_results,

        "internships": internship_results
    }
