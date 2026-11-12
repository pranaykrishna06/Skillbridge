from app.db.postgres import get_postgres_connection


# ============================================================
# 1. CREATE NOTIFICATION
# ============================================================

def create_notification(
    user_id: int,
    title: str,
    message: str,
    notification_type: str,
    related_entity_type: str = None,
    related_entity_id: int = None
):

    connection = get_postgres_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO notifications (
                    user_id,
                    title,
                    message,
                    notification_type,
                    related_entity_type,
                    related_entity_id
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING notification_id, created_at
                """,
                (
                    user_id,
                    title,
                    message,
                    notification_type,
                    related_entity_type,
                    related_entity_id
                )
            )

            notification = cursor.fetchone()

        connection.commit()

        return {
            "notification_id": notification[0],
            "created_at": notification[1]
        }

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()


# ============================================================
# 2. GET USER NOTIFICATIONS
# ============================================================

def get_user_notifications(
    user_id: int,
    limit: int = 20,
    offset: int = 0
):

    connection = get_postgres_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    notification_id,
                    title,
                    message,
                    notification_type,
                    related_entity_type,
                    related_entity_id,
                    is_read,
                    created_at
                FROM notifications
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                (user_id, limit, offset)
            )

            rows = cursor.fetchall()

        notifications = []

        for row in rows:

            notifications.append({

                "notification_id": row[0],
                "title": row[1],
                "message": row[2],
                "notification_type": row[3],
                "related_entity_type": row[4],
                "related_entity_id": row[5],
                "is_read": row[6],
                "created_at": row[7]

            })

        return notifications

    finally:

        connection.close()


# ============================================================
# 3. GET UNREAD NOTIFICATION COUNT
# ============================================================

def get_unread_notification_count(user_id: int):

    connection = get_postgres_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM notifications
                WHERE user_id = %s
                AND is_read = FALSE
                """,
                (user_id,)
            )

            result = cursor.fetchone()

            return result[0]

    finally:

        connection.close()


# ============================================================
# 4. MARK NOTIFICATION AS READ
# ============================================================

def mark_notification_as_read(
    user_id: int,
    notification_id: int
):

    connection = get_postgres_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE notifications
                SET is_read = TRUE
                WHERE notification_id = %s
                AND user_id = %s
                RETURNING notification_id
                """,
                (notification_id, user_id)
            )

            result = cursor.fetchone()

        connection.commit()

        return result is not None

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()


# ============================================================
# 5. MARK ALL NOTIFICATIONS AS READ
# ============================================================

def mark_all_notifications_as_read(user_id: int):

    connection = get_postgres_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE notifications
                SET is_read = TRUE
                WHERE user_id = %s
                AND is_read = FALSE
                """,
                (user_id,)
            )

            updated_count = cursor.rowcount

        connection.commit()

        return updated_count

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()


# ============================================================
# 6. DELETE A NOTIFICATION
# ============================================================

def delete_notification(
    user_id: int,
    notification_id: int
):

    connection = get_postgres_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM notifications
                WHERE notification_id = %s
                AND user_id = %s
                RETURNING notification_id
                """,
                (notification_id, user_id)
            )

            result = cursor.fetchone()

        connection.commit()

        return result is not None

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()
