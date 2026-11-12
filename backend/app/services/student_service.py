import logging

from app.db.postgres import get_postgres_connection
from app.services.learning_sync_service import (
    queue_student_data_sync,
    process_student_data_sync_event
)

logger = logging.getLogger(__name__)


# ==========================================
# AUTOMATIC EMBEDDING REFRESH
# ==========================================

def refresh_student_embedding_safely(student_id):
    """Embedding-based AI matching is disabled in this build.

    The learning synchronization worker still performs Neo4j graph sync;
    this compatibility function marks the embedding step as intentionally
    disabled without importing or downloading an ML model.
    """
    return {
        "status": "disabled",
        "student_id": student_id,
        "message": "AI recommendation embeddings are disabled."
    }

# ==========================================
# LEARNING SYNCHRONIZATION OUTBOX
# ==========================================

def queue_student_skill_sync(cursor, student_id, skill_id):
    """
    Insert a synchronization event into the outbox.

    This function must be called using the same PostgreSQL
    cursor and transaction as the skill modification.
    """

    cursor.execute(
        """
        INSERT INTO learning_sync_outbox (
            student_id,
            skill_id,
            embedding_status,
            graph_status
        )

        VALUES (%s, %s, 'pending', 'pending')

        RETURNING sync_id
        """,
        (student_id, skill_id)
    )

    result = cursor.fetchone()

    return result[0]


def process_student_skill_sync_safely(sync_id):
    """
    Attempt immediate processing of a synchronization event.

    If processing fails, the event remains in PostgreSQL
    and can be retried by the background worker.
    """

    try:

        from app.services.learning_sync_service import (
            process_learning_sync_event
        )

        return process_learning_sync_event(sync_id)

    except Exception:

        logger.exception(
            "Immediate synchronization failed for event %s. "
            "The background worker will retry it.",
            sync_id
        )

        return {
            "sync_id": sync_id,
            "status": "pending"
        }


# ==========================================
# STUDENT PROFILE
# ==========================================

def create_student_profile(student_id, data):

    connection = get_postgres_connection()

    event_id = None

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO students (
                    student_id,
                    registration_number,
                    department,
                    year_of_study,
                    cgpa,
                    graduation_year,
                    bio
                )

                VALUES (%s, %s, %s, %s, %s, %s, %s)

                RETURNING *
                """,
                (
                    student_id,
                    data.registration_number,
                    data.department,
                    data.year_of_study,
                    data.cgpa,
                    data.graduation_year,
                    data.bio
                )
            )

            result = cursor.fetchone()

            event_id = queue_student_data_sync(
                cursor,
                student_id
            )

        connection.commit()

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()

    process_student_data_sync_event(event_id)

    return result


def get_student_profile(student_id):

    connection = get_postgres_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    s.student_id,
                    u.user_id,
                    u.full_name,
                    u.email,
                    s.registration_number,
                    s.department,
                    s.year_of_study,
                    s.cgpa,
                    s.graduation_year,
                    s.bio

                FROM students s

                JOIN users u
                    ON s.student_id = u.user_id

                WHERE s.student_id = %s
                """,
                (student_id,)
            )

            result = cursor.fetchone()

            if not result:
                return None

            return {
                "student_id": result[0],
                "user_id": result[1],
                "full_name": result[2],
                "email": result[3],
                "registration_number": result[4],
                "department": result[5],
                "year_of_study": result[6],
                "cgpa": float(result[7]),
                "graduation_year": result[8],
                "bio": result[9]
            }

    finally:

        connection.close()


def update_student_profile(student_id, data):

    connection = get_postgres_connection()

    event_id = None

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE students

                SET
                    registration_number = %s,
                    department = %s,
                    year_of_study = %s,
                    cgpa = %s,
                    graduation_year = %s,
                    bio = %s

                WHERE student_id = %s

                RETURNING student_id
                """,
                (
                    data.registration_number,
                    data.department,
                    data.year_of_study,
                    data.cgpa,
                    data.graduation_year,
                    data.bio,
                    student_id
                )
            )

            result = cursor.fetchone()

            if result:

                event_id = queue_student_data_sync(
                    cursor,
                    student_id
                )

        connection.commit()

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()

    if event_id is not None:
        process_student_data_sync_event(event_id)

    return result is not None

# ==========================================
# STUDENT SKILLS
# ==========================================

def get_student_skills(student_id):

    connection = get_postgres_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    sk.skill_id,
                    sk.skill_name,
                    sk.skill_category,
                    ss.proficiency_level,
                    ss.years_experience,
                    ss.last_used_date

                FROM student_skills ss

                JOIN skills sk
                    ON ss.skill_id = sk.skill_id

                WHERE ss.student_id = %s

                ORDER BY sk.skill_name
                """,
                (student_id,)
            )

            results = cursor.fetchall()

            return [
                {
                    "skill_id": row[0],
                    "skill_name": row[1],
                    "skill_category": row[2],
                    "proficiency_level": row[3],
                    "years_experience": float(row[4]),
                    "last_used_date": row[5]
                }
                for row in results
            ]

    finally:

        connection.close()


def add_student_skill(student_id, data):

    connection = get_postgres_connection()

    sync_id = None

    try:

        with connection.cursor() as cursor:

            # ------------------------------------------
            # 1. Add or update student skill
            # ------------------------------------------

            cursor.execute(
                """
                INSERT INTO student_skills (
                    student_id,
                    skill_id,
                    proficiency_level,
                    years_experience,
                    last_used_date
                )

                VALUES (%s, %s, %s, %s, %s)

                ON CONFLICT (student_id, skill_id)

                DO UPDATE SET

                    proficiency_level = EXCLUDED.proficiency_level,
                    years_experience = EXCLUDED.years_experience,
                    last_used_date = EXCLUDED.last_used_date

                RETURNING skill_id
                """,
                (
                    student_id,
                    data.skill_id,
                    data.proficiency_level,
                    data.years_experience,
                    data.last_used_date
                )
            )

            result = cursor.fetchone()

            # ------------------------------------------
            # 2. Create synchronization event
            # ------------------------------------------

            if result:

                sync_id = queue_student_skill_sync(
                    cursor,
                    student_id,
                    data.skill_id
                )

        # ------------------------------------------
        # 3. Commit skill and outbox together
        # ------------------------------------------

        connection.commit()

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()

    # ------------------------------------------
    # 4. Attempt immediate synchronization
    # ------------------------------------------

    if sync_id is not None:

        process_student_skill_sync_safely(sync_id)

    return result is not None


def delete_student_skill(student_id, skill_id):

    connection = get_postgres_connection()

    sync_id = None

    try:

        with connection.cursor() as cursor:

            # ------------------------------------------
            # 1. Delete student skill
            # ------------------------------------------

            cursor.execute(
                """
                DELETE FROM student_skills

                WHERE student_id = %s
                  AND skill_id = %s

                RETURNING skill_id
                """,
                (student_id, skill_id)
            )

            result = cursor.fetchone()

            # ------------------------------------------
            # 2. Create synchronization event
            # ------------------------------------------

            if result:

                sync_id = queue_student_skill_sync(
                    cursor,
                    student_id,
                    skill_id
                )

        # ------------------------------------------
        # 3. Commit deletion and outbox together
        # ------------------------------------------

        connection.commit()

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()

    # ------------------------------------------
    # 4. Attempt immediate synchronization
    # ------------------------------------------

    if sync_id is not None:

        process_student_skill_sync_safely(sync_id)

    return result is not None


# ==========================================
# STUDENT PROJECTS
# ==========================================

def get_student_projects(student_id):

    connection = get_postgres_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    project_id,
                    project_title,
                    project_description,
                    project_url,
                    start_date,
                    end_date

                FROM student_projects

                WHERE student_id = %s

                ORDER BY project_id DESC
                """,
                (student_id,)
            )

            results = cursor.fetchall()

            return [
                {
                    "project_id": row[0],
                    "project_title": row[1],
                    "project_description": row[2],
                    "project_url": row[3],
                    "start_date": row[4],
                    "end_date": row[5]
                }
                for row in results
            ]

    finally:

        connection.close()


def add_student_project(student_id, data):

    connection = get_postgres_connection()

    event_id = None

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO student_projects (
                    student_id,
                    project_title,
                    project_description,
                    project_url,
                    start_date,
                    end_date
                )

                VALUES (%s, %s, %s, %s, %s, %s)

                RETURNING project_id
                """,
                (
                    student_id,
                    data.project_title,
                    data.project_description,
                    data.project_url,
                    data.start_date,
                    data.end_date
                )
            )

            result = cursor.fetchone()

            if result:

                event_id = queue_student_data_sync(
                    cursor,
                    student_id
                )

        connection.commit()

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()

    if event_id is not None:
        process_student_data_sync_event(event_id)

    return result[0]

def delete_student_project(student_id, project_id):

    connection = get_postgres_connection()

    event_id = None

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM student_projects

                WHERE student_id = %s
                  AND project_id = %s

                RETURNING project_id
                """,
                (student_id, project_id)
            )

            result = cursor.fetchone()

            if result:

                event_id = queue_student_data_sync(
                    cursor,
                    student_id
                )

        connection.commit()

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()

    if event_id is not None:
        process_student_data_sync_event(event_id)

    return result is not None