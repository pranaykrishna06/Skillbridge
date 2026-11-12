from app.db.postgres import get_postgres_connection
import logging

from app.db.postgres import get_postgres_connection

logger = logging.getLogger(__name__)

# ============================================================
# LEARNING PROGRESS SERVICE
# ============================================================

VALID_STATUSES = [
    "Not Started",
    "In Progress",
    "Completed"
]


# ============================================================
# UPDATE LEARNING PROGRESS
# ============================================================

import logging

from app.db.postgres import get_postgres_connection
from app.services.learning_sync_service import (
    process_learning_sync_event
)

logger = logging.getLogger(__name__)

VALID_STATUSES = {
    "Not Started",
    "In Progress",
    "Completed"
}


def update_learning_progress(
    student_id: int,
    skill_id: int,
    progress_status: str,
    notes: str | None = None,
    proficiency_level: int | None = None
):
    """
    Update learning progress and optionally update proficiency.

    Synchronization work is inserted into the outbox in the
    same PostgreSQL transaction as the learning-progress update.

    Failed embedding or Neo4j operations remain available
    for background retry.
    """

    if progress_status not in VALID_STATUSES:
        raise ValueError("Invalid learning progress status.")

    if proficiency_level is not None:

        if (
            isinstance(proficiency_level, bool)
            or not isinstance(proficiency_level, int)
            or not 1 <= proficiency_level <= 5
        ):
            raise ValueError(
                "Proficiency level must be an integer between 1 and 5."
            )

    connection = get_postgres_connection()

    sync_id = None

    try:
        with connection.cursor() as cursor:

            # -------------------------------------------------
            # 1. Validate student
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT student_id
                FROM students
                WHERE student_id = %s
                """,
                (student_id,)
            )

            if cursor.fetchone() is None:
                raise ValueError("Student does not exist.")

            # -------------------------------------------------
            # 2. Validate active skill
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT skill_id
                FROM skills
                WHERE skill_id = %s
                  AND is_active = TRUE
                """,
                (skill_id,)
            )

            if cursor.fetchone() is None:
                raise ValueError("Skill does not exist or is inactive.")

            # -------------------------------------------------
            # 3. Insert or update learning progress
            # -------------------------------------------------

            cursor.execute(
                """
                INSERT INTO learning_progress (
                    student_id,
                    skill_id,
                    progress_status,
                    notes,
                    started_at,
                    completed_at,
                    updated_at
                )

                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,

                    CASE
                        WHEN %s = 'Not Started'
                        THEN NULL
                        ELSE CURRENT_TIMESTAMP
                    END,

                    CASE
                        WHEN %s = 'Completed'
                        THEN CURRENT_TIMESTAMP
                        ELSE NULL
                    END,

                    CURRENT_TIMESTAMP
                )

                ON CONFLICT (student_id, skill_id)

                DO UPDATE SET

                    progress_status = EXCLUDED.progress_status,

                    notes = EXCLUDED.notes,

                    started_at = CASE
                        WHEN EXCLUDED.progress_status = 'Not Started'
                        THEN NULL
                        ELSE COALESCE(
                            learning_progress.started_at,
                            CURRENT_TIMESTAMP
                        )
                    END,

                    completed_at = CASE
                        WHEN EXCLUDED.progress_status = 'Completed'
                        THEN CURRENT_TIMESTAMP
                        ELSE NULL
                    END,

                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    student_id,
                    skill_id,
                    progress_status,
                    notes,
                    progress_status,
                    progress_status
                )
            )

            # -------------------------------------------------
            # 4. Update student proficiency when provided
            # -------------------------------------------------

            if proficiency_level is not None:

                cursor.execute(
                    """
                    INSERT INTO student_skills (
                        student_id,
                        skill_id,
                        proficiency_level
                    )

                    VALUES (%s, %s, %s)

                    ON CONFLICT (student_id, skill_id)

                    DO UPDATE SET
                        proficiency_level = EXCLUDED.proficiency_level
                    """,
                    (
                        student_id,
                        skill_id,
                        proficiency_level
                    )
                )

                # -------------------------------------------------
                # 5. Create durable synchronization event
                # -------------------------------------------------

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

                sync_id = cursor.fetchone()[0]

        # Commit progress, proficiency and outbox together.
        connection.commit()

    except Exception:
        connection.rollback()
        logger.exception(
            "Failed to update learning progress for student %s",
            student_id
        )
        raise

    finally:
        connection.close()

    # ---------------------------------------------------------
    # 6. Attempt immediate synchronization
    # ---------------------------------------------------------

    sync_result = None

    if sync_id is not None:

        try:
            sync_result = process_learning_sync_event(sync_id)

        except Exception:

            # The database transaction has already committed.
            # The event remains in the outbox for background retry.

            logger.exception(
                "Immediate synchronization failed for event %s. "
                "Background retry will handle it.",
                sync_id
            )

            sync_result = {
                "sync_id": sync_id,
                "status": "pending"
            }

    return {
        "student_id": student_id,
        "skill_id": skill_id,
        "progress_status": progress_status,
        "notes": notes,
        "proficiency_level": proficiency_level,
        "sync_id": sync_id,
        "synchronization": sync_result
    }
# ============================================================
# GET STUDENT LEARNING PROGRESS
# ============================================================

def get_student_learning_progress(student_id: int):

    connection = get_postgres_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    lp.progress_id,
                    lp.skill_id,
                    sk.skill_name,
                    lp.progress_status,
                    lp.notes,
                    lp.started_at,
                    lp.completed_at,
                    lp.updated_at,
                    ss.proficiency_level

                FROM learning_progress AS lp

                JOIN skills AS sk
                    ON lp.skill_id = sk.skill_id

                LEFT JOIN student_skills AS ss
                    ON lp.student_id = ss.student_id
                    AND lp.skill_id = ss.skill_id

                WHERE lp.student_id = %s

                ORDER BY lp.updated_at DESC
                """,
                (student_id,)
            )

            rows = cursor.fetchall()

            return [
                {
                    "progress_id": row[0],
                    "skill_id": row[1],
                    "skill_name": row[2],
                    "progress_status": row[3],
                    "notes": row[4],
                    "started_at": row[5],
                    "completed_at": row[6],
                    "updated_at": row[7],
                    "proficiency_level": row[8]
                }
                for row in rows
            ]

    finally:

        connection.close()


# ============================================================
# GET LEARNING PROGRESS SUMMARY
# ============================================================

def get_learning_progress_summary(student_id: int):

    connection = get_postgres_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total_skills,

                    COUNT(*) FILTER (
                        WHERE progress_status = 'Not Started'
                    ) AS not_started,

                    COUNT(*) FILTER (
                        WHERE progress_status = 'In Progress'
                    ) AS in_progress,

                    COUNT(*) FILTER (
                        WHERE progress_status = 'Completed'
                    ) AS completed

                FROM learning_progress

                WHERE student_id = %s
                """,
                (student_id,)
            )

            row = cursor.fetchone()

            total = row[0] or 0
            not_started = row[1] or 0
            in_progress = row[2] or 0
            completed = row[3] or 0

            completion_percentage = (
                round((completed / total) * 100, 2)
                if total > 0
                else 0
            )

            return {
                "student_id": student_id,
                "total_tracked_skills": total,
                "not_started": not_started,
                "in_progress": in_progress,
                "completed": completed,
                "completion_percentage": completion_percentage
            }

    finally:

        connection.close()