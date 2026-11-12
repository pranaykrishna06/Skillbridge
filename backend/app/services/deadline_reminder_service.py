from app.db.postgres import get_postgres_connection


# ==========================================
# SEND INTERNSHIP DEADLINE REMINDERS
# ==========================================

def send_deadline_reminders():

    connection = get_postgres_connection()

    reminders_created = 0

    try:
        with connection.cursor() as cursor:

            # ----------------------------------
            # 3-DAY DEADLINE REMINDERS
            # ----------------------------------

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
                SELECT
                    si.student_id,
                    'Internship Deadline Approaching',
                    'The application deadline for '
                        || i.title
                        || ' is in 3 days. Apply before the deadline.',
                    'deadline_reminder',
                    'deadline_3_days',
                    i.internship_id
                FROM saved_internships si
                JOIN internships i
                    ON si.internship_id = i.internship_id
                WHERE i.status = 'Open'
                  AND i.application_deadline = CURRENT_DATE + 3
                  AND NOT EXISTS (
                      SELECT 1
                      FROM notifications n
                      WHERE n.user_id = si.student_id
                        AND n.related_entity_type = 'deadline_3_days'
                        AND n.related_entity_id = i.internship_id
                  )
                  AND NOT EXISTS (
                      SELECT 1
                      FROM applications a
                      WHERE a.student_id = si.student_id
                        AND a.internship_id = i.internship_id
                  )
                RETURNING notification_id
                """
            )

            three_day_results = cursor.fetchall()

            reminders_created += len(three_day_results)

            # ----------------------------------
            # 1-DAY DEADLINE REMINDERS
            # ----------------------------------

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
                SELECT
                    si.student_id,
                    'Internship Deadline Tomorrow',
                    'The application deadline for '
                        || i.title
                        || ' is tomorrow. Apply now if you are interested.',
                    'deadline_reminder',
                    'deadline_1_day',
                    i.internship_id
                FROM saved_internships si
                JOIN internships i
                    ON si.internship_id = i.internship_id
                WHERE i.status = 'Open'
                  AND i.application_deadline = CURRENT_DATE + 1
                  AND NOT EXISTS (
                      SELECT 1
                      FROM notifications n
                      WHERE n.user_id = si.student_id
                        AND n.related_entity_type = 'deadline_1_day'
                        AND n.related_entity_id = i.internship_id
                  )
                  AND NOT EXISTS (
                      SELECT 1
                      FROM applications a
                      WHERE a.student_id = si.student_id
                        AND a.internship_id = i.internship_id
                  )
                RETURNING notification_id
                """
            )

            one_day_results = cursor.fetchall()

            reminders_created += len(one_day_results)

            connection.commit()

            return {
                "success": True,
                "reminders_created": reminders_created,
                "three_day_reminders": len(three_day_results),
                "one_day_reminders": len(one_day_results)
            }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
