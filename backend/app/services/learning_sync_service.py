import logging

from app.db.postgres import get_postgres_connection

logger = logging.getLogger(__name__)


def process_learning_sync_event(sync_id: int):
    """
    Process one pending learning synchronization event.

    Embedding and Neo4j synchronization are handled independently.
    If one fails, the other can still succeed.
    """

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE learning_sync_outbox
                SET locked_until = CURRENT_TIMESTAMP + INTERVAL '5 minutes',
                    updated_at = CURRENT_TIMESTAMP
                WHERE sync_id = %s
                  AND (
                      embedding_status = 'pending'
                      OR graph_status = 'pending'
                  )
                  AND next_attempt_at <= CURRENT_TIMESTAMP
                  AND (
                      locked_until IS NULL
                      OR locked_until < CURRENT_TIMESTAMP
                  )
                RETURNING
                    sync_id,
                    student_id,
                    skill_id,
                    embedding_status,
                    graph_status
                """,
                (sync_id,)
            )

            event = cursor.fetchone()

        connection.commit()

    except Exception:
        connection.rollback()
        logger.exception(
            "Failed to claim synchronization event %s",
            sync_id
        )
        raise

    finally:
        connection.close()

    if event is None:
        return {
            "sync_id": sync_id,
            "status": "not_claimed",
            "message": "Event is unavailable, already completed, or waiting for retry."
        }

    (
        event_id,
        student_id,
        skill_id,
        embedding_status,
        graph_status
    ) = event

    embedding_success = embedding_status == "completed"
    graph_success = graph_status == "completed"

    # ---------------------------------------------------------
    # 1. Update student embedding
    # ---------------------------------------------------------

    if embedding_status == "pending":

        try:
            from app.services.student_service import (
                refresh_student_embedding_safely
            )

            refresh_student_embedding_safely(student_id)

            embedding_success = True

            _update_sync_result(
                event_id,
                operation="embedding",
                success=True
            )

            logger.info(
                "Embedding refreshed for student %s",
                student_id
            )

        except Exception as error:

            logger.exception(
                "Embedding refresh failed for student %s",
                student_id
            )

            _update_sync_result(
                event_id,
                operation="embedding",
                success=False,
                error=str(error)
            )

    # ---------------------------------------------------------
    # 2. Synchronize student skill with Neo4j
    # ---------------------------------------------------------

    if graph_status == "pending":

        try:
            from app.services.graph_sync_service import (
                synchronize_student_skill
            )

            synchronize_student_skill(
                student_id=student_id,
                skill_id=skill_id
            )

            graph_success = True

            _update_sync_result(
                event_id,
                operation="graph",
                success=True
            )

            logger.info(
                "Neo4j skill synchronized for student %s, skill %s",
                student_id,
                skill_id
            )

        except Exception as error:

            logger.exception(
                "Neo4j synchronization failed for student %s, skill %s",
                student_id,
                skill_id
            )

            _update_sync_result(
                event_id,
                operation="graph",
                success=False,
                error=str(error)
            )

    # ---------------------------------------------------------
    # 3. Finalize event
    # ---------------------------------------------------------

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE learning_sync_outbox
                SET
                    completed_at = CASE
                        WHEN embedding_status = 'completed'
                         AND graph_status = 'completed'
                        THEN CURRENT_TIMESTAMP
                        ELSE NULL
                    END,

                    locked_until = NULL,

                    updated_at = CURRENT_TIMESTAMP

                WHERE sync_id = %s
                """,
                (event_id,)
            )

            cursor.execute(
                """
                SELECT embedding_status, graph_status
                FROM learning_sync_outbox
                WHERE sync_id = %s
                """,
                (event_id,)
            )

            final_status = cursor.fetchone()

        connection.commit()

    except Exception:
        connection.rollback()
        logger.exception(
            "Failed to finalize synchronization event %s",
            event_id
        )
        raise

    finally:
        connection.close()

    if final_status is None:
        return {
            "sync_id": event_id,
            "status": "unknown"
        }

    final_embedding_status, final_graph_status = final_status

    completed = (
        final_embedding_status == "completed"
        and final_graph_status == "completed"
    )

    return {
        "sync_id": event_id,
        "student_id": student_id,
        "skill_id": skill_id,
        "embedding_status": final_embedding_status,
        "graph_status": final_graph_status,
        "status": "completed" if completed else "pending"
    }


def _update_sync_result(
    sync_id: int,
    operation: str,
    success: bool,
    error: str | None = None
):
    """
    Record the result of an individual synchronization operation.
    """

    if operation not in ("embedding", "graph"):
        raise ValueError("Invalid synchronization operation.")

    status_column = f"{operation}_status"
    attempts_column = f"{operation}_attempts"
    error_column = f"{operation}_last_error"

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            if success:

                cursor.execute(
                    f"""
                    UPDATE learning_sync_outbox
                    SET
                        {status_column} = 'completed',
                        {error_column} = NULL,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE sync_id = %s
                    """,
                    (sync_id,)
                )

            else:

                cursor.execute(
                    f"""
                    UPDATE learning_sync_outbox
                    SET
                        {attempts_column} = {attempts_column} + 1,

                        {error_column} = %s,

                        next_attempt_at =
                            CURRENT_TIMESTAMP
                            + (
                                LEAST(
                                    360,
                                    POWER(
                                        2,
                                        LEAST({attempts_column} + 1, 9)
                                    )
                                )::INTEGER
                                * INTERVAL '1 minute'
                            ),

                        updated_at = CURRENT_TIMESTAMP

                    WHERE sync_id = %s
                    """,
                    (error, sync_id)
                )

        connection.commit()

    except Exception:
        connection.rollback()
        logger.exception(
            "Could not record %s synchronization result for event %s",
            operation,
            sync_id
        )
        raise

    finally:
        connection.close()


def process_pending_sync_events(limit: int = 20):
    """
    Process pending synchronization events.

    Multiple workers can run safely because events are claimed
    using database row locks and a temporary processing lease.
    """

    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT sync_id
                FROM learning_sync_outbox
                WHERE (
                    embedding_status = 'pending'
                    OR graph_status = 'pending'
                )
                  AND next_attempt_at <= CURRENT_TIMESTAMP
                  AND (
                      locked_until IS NULL
                      OR locked_until < CURRENT_TIMESTAMP
                  )
                ORDER BY created_at ASC
                LIMIT %s
                """,
                (limit,)
            )

            event_ids = [row[0] for row in cursor.fetchall()]

    finally:
        connection.close()

    results = []

    for event_id in event_ids:

        try:
            result = process_learning_sync_event(event_id)
            results.append(result)

        except Exception as error:

            logger.exception(
                "Failed to process synchronization event %s",
                event_id
            )

            results.append({
                "sync_id": event_id,
                "status": "error",
                "error": str(error)
            })

    return {
        "processed": len(results),
        "results": results
    }


def get_learning_sync_status(student_id: int):
    """
    Return synchronization history for one student.
    """

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    sync_id,
                    student_id,
                    skill_id,
                    embedding_status,
                    graph_status,
                    embedding_attempts,
                    graph_attempts,
                    embedding_last_error,
                    graph_last_error,
                    next_attempt_at,
                    created_at,
                    updated_at,
                    completed_at

                FROM learning_sync_outbox

                WHERE student_id = %s

                ORDER BY created_at DESC
                """,
                (student_id,)
            )

            rows = cursor.fetchall()

            columns = [
                description[0]
                for description in cursor.description
            ]

            return [
                dict(zip(columns, row))
                for row in rows
            ]

    finally:
        connection.close()
        
def queue_student_data_sync(cursor, student_id: int):
    """
    Insert a student-wide synchronization event.

    Must be called within the same PostgreSQL transaction
    as the profile or project modification.
    """

    cursor.execute(
        """
        INSERT INTO student_data_sync_outbox (
            student_id,
            embedding_status,
            graph_status
        )
        VALUES (%s, 'pending', 'pending')
        RETURNING event_id
        """,
        (student_id,)
    )

    return cursor.fetchone()[0]


def _update_student_data_sync_result(
    event_id: int,
    operation: str,
    success: bool,
    error: str | None = None
):
    """
    Record embedding or graph synchronization results.
    """

    if operation not in ("embedding", "graph"):
        raise ValueError("Invalid synchronization operation.")

    status_column = f"{operation}_status"
    attempts_column = f"{operation}_attempts"
    error_column = f"{operation}_last_error"

    connection = get_postgres_connection()

    try:

        with connection.cursor() as cursor:

            if success:

                cursor.execute(
                    f"""
                    UPDATE student_data_sync_outbox

                    SET
                        {status_column} = 'completed',
                        {error_column} = NULL,
                        updated_at = CURRENT_TIMESTAMP

                    WHERE event_id = %s
                    """,
                    (event_id,)
                )

            else:

                cursor.execute(
                    f"""
                    UPDATE student_data_sync_outbox

                    SET
                        {attempts_column} = {attempts_column} + 1,
                        {error_column} = %s,

                        next_attempt_at =
                            CURRENT_TIMESTAMP
                            + (
                                LEAST(
                                    360,
                                    POWER(
                                        2,
                                        LEAST({attempts_column} + 1, 9)
                                    )
                                )::INTEGER
                                * INTERVAL '1 minute'
                            ),

                        updated_at = CURRENT_TIMESTAMP

                    WHERE event_id = %s
                    """,
                    (error, event_id)
                )

        connection.commit()

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()


def process_student_data_sync_event(event_id: int):
    """
    Process a student profile/project synchronization event.

    Embeddings and Neo4j graph synchronization are independent.
    """

    connection = get_postgres_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE student_data_sync_outbox

                SET
                    locked_until =
                        CURRENT_TIMESTAMP + INTERVAL '5 minutes',

                    updated_at = CURRENT_TIMESTAMP

                WHERE event_id = %s

                  AND (
                      embedding_status = 'pending'
                      OR graph_status = 'pending'
                  )

                  AND next_attempt_at <= CURRENT_TIMESTAMP

                  AND (
                      locked_until IS NULL
                      OR locked_until < CURRENT_TIMESTAMP
                  )

                RETURNING
                    student_id,
                    embedding_status,
                    graph_status
                """,
                (event_id,)
            )

            event = cursor.fetchone()

        connection.commit()

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()

    if event is None:

        return {
            "event_id": event_id,
            "status": "not_claimed"
        }

    student_id, embedding_status, graph_status = event

    # -----------------------------------------------------
    # 1. Refresh embedding
    # -----------------------------------------------------

    if embedding_status == "pending":

        try:

            from app.services.student_service import (
                refresh_student_embedding_safely
            )

            refresh_student_embedding_safely(student_id)

            _update_student_data_sync_result(
                event_id,
                "embedding",
                True
            )

        except Exception as error:

            logger.exception(
                "Student embedding refresh failed for student %s",
                student_id
            )

            _update_student_data_sync_result(
                event_id,
                "embedding",
                False,
                str(error)
            )

    # -----------------------------------------------------
    # 2. Synchronize complete Neo4j graph
    # -----------------------------------------------------

    if graph_status == "pending":

        try:

            from app.services.graph_sync_service import (
                synchronize_graph
            )

            synchronize_graph()

            _update_student_data_sync_result(
                event_id,
                "graph",
                True
            )

        except Exception as error:

            logger.exception(
                "Full graph synchronization failed for student %s",
                student_id
            )

            _update_student_data_sync_result(
                event_id,
                "graph",
                False,
                str(error)
            )

    # -----------------------------------------------------
    # 3. Finalize event
    # -----------------------------------------------------

    connection = get_postgres_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE student_data_sync_outbox

                SET
                    completed_at = CASE

                        WHEN embedding_status = 'completed'
                         AND graph_status = 'completed'

                        THEN CURRENT_TIMESTAMP

                        ELSE NULL

                    END,

                    locked_until = NULL,

                    updated_at = CURRENT_TIMESTAMP

                WHERE event_id = %s
                """,
                (event_id,)
            )

            cursor.execute(
                """
                SELECT embedding_status, graph_status

                FROM student_data_sync_outbox

                WHERE event_id = %s
                """,
                (event_id,)
            )

            final_status = cursor.fetchone()

        connection.commit()

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()

    completed = (
        final_status is not None
        and final_status[0] == "completed"
        and final_status[1] == "completed"
    )

    return {
        "event_id": event_id,
        "student_id": student_id,
        "embedding_status": final_status[0],
        "graph_status": final_status[1],
        "status": "completed" if completed else "pending"
    }


def process_pending_student_data_sync_events(limit: int = 20):
    """
    Process pending student profile/project synchronization events.
    """

    connection = get_postgres_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT event_id

                FROM student_data_sync_outbox

                WHERE (
                    embedding_status = 'pending'
                    OR graph_status = 'pending'
                )

                AND next_attempt_at <= CURRENT_TIMESTAMP

                AND (
                    locked_until IS NULL
                    OR locked_until < CURRENT_TIMESTAMP
                )

                ORDER BY created_at ASC

                LIMIT %s
                """,
                (limit,)
            )

            event_ids = [
                row[0]
                for row in cursor.fetchall()
            ]

    finally:

        connection.close()

    results = []

    for event_id in event_ids:

        try:

            results.append(
                process_student_data_sync_event(event_id)
            )

        except Exception as error:

            logger.exception(
                "Student data synchronization failed for event %s",
                event_id
            )

            results.append({
                "event_id": event_id,
                "status": "error",
                "error": str(error)
            })

    return {
        "processed": len(results),
        "results": results
    }
def get_student_data_sync_status(student_id: int):
    """
    Retrieve synchronization history for student profile
    and project changes.
    """

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    event_id,
                    student_id,
                    embedding_status,
                    graph_status,
                    embedding_attempts,
                    graph_attempts,
                    embedding_last_error,
                    graph_last_error,
                    next_attempt_at,
                    locked_until,
                    created_at,
                    updated_at,
                    completed_at

                FROM student_data_sync_outbox

                WHERE student_id = %s

                ORDER BY created_at DESC
                """,
                (student_id,)
            )

            rows = cursor.fetchall()

            columns = [
                description[0]
                for description in cursor.description
            ]

            return [
                dict(zip(columns, row))
                for row in rows
            ]

    finally:
        connection.close()