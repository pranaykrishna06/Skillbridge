from app.db.postgres import get_postgres_connection


# ==========================================
# NOTIFICATION HELPER
# ==========================================

def _create_application_notification(
    cursor,
    user_id,
    title,
    message,
    application_id
):
    """
    Create an in-app notification for an application event.

    Uses the existing database cursor so the notification
    and application update are committed together.
    """

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
        """,
        (
            user_id,
            title,
            message,
            "application",
            "application",
            application_id
        )
    )


# ==========================================
# VIEW AVAILABLE INTERNSHIPS
# ==========================================

def get_available_internships(student_id):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    i.internship_id,
                    i.title,
                    i.description,
                    c.company_name,
                    i.work_mode,
                    i.location,
                    i.stipend,
                    i.duration_months,
                    i.minimum_cgpa,
                    i.minimum_year,
                    i.application_deadline
                FROM internships i
                JOIN companies c ON i.company_id = c.company_id
                WHERE i.status = 'Open'
                  AND i.application_deadline >= CURRENT_DATE
                  AND i.available_positions > 0
                  AND NOT EXISTS (
                      SELECT 1
                      FROM applications a
                      WHERE a.student_id = %s
                        AND a.internship_id = i.internship_id
                  )
                ORDER BY i.created_at DESC
                """,
                (student_id,)
            )

            rows = cursor.fetchall()

            return [
                {
                    "internship_id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "company_name": row[3],
                    "work_mode": row[4],
                    "location": row[5],
                    "stipend": float(row[6]),
                    "duration_months": row[7],
                    "minimum_cgpa": float(row[8]),
                    "minimum_year": row[9],
                    "application_deadline": row[10]
                }
                for row in rows
            ]

    finally:
        connection.close()


# ==========================================
# APPLY FOR INTERNSHIP
# ==========================================

def apply_for_internship(student_id, data):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    s.cgpa,
                    s.year_of_study,
                    i.minimum_cgpa,
                    i.minimum_year,
                    i.application_deadline,
                    i.available_positions,
                    i.status,
                    i.title
                FROM students s
                CROSS JOIN internships i
                WHERE s.student_id = %s
                  AND i.internship_id = %s
                FOR UPDATE OF i
                """,
                (student_id, data.internship_id)
            )

            internship = cursor.fetchone()

            if not internship:
                return {
                    "error": "Student profile or internship not found."
                }

            (
                cgpa,
                year,
                min_cgpa,
                min_year,
                deadline,
                positions,
                status,
                internship_title
            ) = internship

            if status != "Open":
                return {"error": "Internship is not open."}

            if deadline is None:
                return {"error": "Invalid application deadline."}

            cursor.execute("SELECT CURRENT_DATE")
            today = cursor.fetchone()[0]

            if deadline < today:
                return {
                    "error": "Application deadline has passed."
                }

            if positions <= 0:
                return {
                    "error": "No positions are available."
                }

            if cgpa < min_cgpa or year < min_year:
                return {
                    "error": "You do not meet the academic eligibility requirements."
                }

            cursor.execute(
                """
                INSERT INTO applications (
                    student_id,
                    internship_id,
                    resume_reference,
                    cover_letter,
                    status
                )
                VALUES (%s, %s, %s, %s, 'Applied')
                RETURNING application_id
                """,
                (
                    student_id,
                    data.internship_id,
                    data.resume_reference,
                    data.cover_letter
                )
            )

            application_id = cursor.fetchone()[0]

            # Create notification for the student.
            _create_application_notification(
                cursor=cursor,
                user_id=student_id,
                title="Application Submitted",
                message=(
                    f"Your application for '{internship_title}' "
                    f"has been submitted successfully."
                ),
                application_id=application_id
            )

            connection.commit()

            return {
                "application_id": application_id,
                "status": "Applied"
            }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ==========================================
# VIEW STUDENT APPLICATIONS
# ==========================================

def get_student_applications(student_id):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    a.application_id,
                    i.internship_id,
                    i.title,
                    c.company_name,
                    a.match_score,
                    a.status,
                    a.applied_at
                FROM applications a
                JOIN internships i ON a.internship_id = i.internship_id
                JOIN companies c ON i.company_id = c.company_id
                WHERE a.student_id = %s
                ORDER BY a.applied_at DESC
                """,
                (student_id,)
            )

            rows = cursor.fetchall()

            return [
                {
                    "application_id": row[0],
                    "internship_id": row[1],
                    "internship_title": row[2],
                    "company_name": row[3],
                    "match_score": float(row[4]) if row[4] is not None else None,
                    "status": row[5],
                    "applied_at": row[6]
                }
                for row in rows
            ]

    finally:
        connection.close()


# ==========================================
# VIEW APPLICATION DETAILS
# ==========================================

def get_application_details(application_id, student_id=None):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            query = """
                SELECT
                    a.application_id,
                    a.student_id,
                    a.internship_id,
                    i.title,
                    c.company_name,
                    a.resume_reference,
                    a.cover_letter,
                    a.match_score,
                    a.status,
                    a.applied_at,
                    a.updated_at
                FROM applications a
                JOIN internships i ON a.internship_id = i.internship_id
                JOIN companies c ON i.company_id = c.company_id
                WHERE a.application_id = %s
            """

            params = [application_id]

            if student_id is not None:
                query += " AND a.student_id = %s"
                params.append(student_id)

            cursor.execute(query, tuple(params))

            row = cursor.fetchone()

            if not row:
                return None

            return {
                "application_id": row[0],
                "student_id": row[1],
                "internship_id": row[2],
                "internship_title": row[3],
                "company_name": row[4],
                "resume_reference": row[5],
                "cover_letter": row[6],
                "match_score": float(row[7]) if row[7] is not None else None,
                "status": row[8],
                "applied_at": row[9],
                "updated_at": row[10]
            }

    finally:
        connection.close()


# ==========================================
# WITHDRAW APPLICATION
# ==========================================

def withdraw_application(application_id, student_id):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    a.status,
                    i.title
                FROM applications a
                JOIN internships i
                    ON a.internship_id = i.internship_id
                WHERE a.application_id = %s
                  AND a.student_id = %s
                FOR UPDATE OF a
                """,
                (application_id, student_id)
            )

            result = cursor.fetchone()

            if not result:
                return "not_found"

            current_status = result[0]
            internship_title = result[1]

            if current_status in (
                "Selected",
                "Rejected",
                "Withdrawn"
            ):
                return "invalid_status"

            cursor.execute(
                "SELECT set_config('app.user_id', %s, true)",
                (str(student_id),)
            )

            cursor.execute(
                """
                UPDATE applications
                SET status = 'Withdrawn'
                WHERE application_id = %s
                  AND student_id = %s
                """,
                (application_id, student_id)
            )

            # Notify the student about the withdrawal.
            _create_application_notification(
                cursor=cursor,
                user_id=student_id,
                title="Application Withdrawn",
                message=(
                    f"Your application for '{internship_title}' "
                    f"has been withdrawn successfully."
                ),
                application_id=application_id
            )

            connection.commit()

            return "success"

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ==========================================
# RECRUITER VIEW APPLICATIONS
# ==========================================

def get_recruiter_applications(recruiter_id):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    a.application_id,
                    u.full_name,
                    u.email,
                    i.internship_id,
                    i.title,
                    a.match_score,
                    a.status,
                    a.applied_at
                FROM applications a
                JOIN students s ON a.student_id = s.student_id
                JOIN users u ON s.student_id = u.user_id
                JOIN internships i ON a.internship_id = i.internship_id
                WHERE i.created_by = %s
                ORDER BY a.applied_at DESC
                """,
                (recruiter_id,)
            )

            rows = cursor.fetchall()

            return [
                {
                    "application_id": row[0],
                    "student_name": row[1],
                    "student_email": row[2],
                    "internship_id": row[3],
                    "internship_title": row[4],
                    "match_score": float(row[5]) if row[5] is not None else None,
                    "status": row[6],
                    "applied_at": row[7]
                }
                for row in rows
            ]

    finally:
        connection.close()


# ==========================================
# UPDATE APPLICATION STATUS
# ==========================================

def update_application_status(
    application_id,
    recruiter_id,
    new_status,
    remarks
):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    a.status,
                    a.student_id,
                    i.title
                FROM applications a
                JOIN internships i
                    ON a.internship_id = i.internship_id
                WHERE a.application_id = %s
                  AND i.created_by = %s
                FOR UPDATE OF a
                """,
                (application_id, recruiter_id)
            )

            result = cursor.fetchone()

            if not result:
                return False

            old_status = result[0]
            student_id = result[1]
            internship_title = result[2]

            if old_status in (
                "Withdrawn",
                "Selected",
                "Rejected"
            ):
                return "terminal"

            if old_status == new_status:
                return "same"

            cursor.execute(
                "SELECT set_config('app.user_id', %s, true)",
                (str(recruiter_id),)
            )

            cursor.execute(
                """
                UPDATE applications
                SET status = %s
                WHERE application_id = %s
                """,
                (new_status, application_id)
            )

            cursor.execute(
                """
                UPDATE application_status_history
                SET remarks = %s
                WHERE application_id = %s
                  AND history_id = (
                      SELECT history_id
                      FROM application_status_history
                      WHERE application_id = %s
                      ORDER BY changed_at DESC, history_id DESC
                      LIMIT 1
                  )
                """,
                (remarks, application_id, application_id)
            )

            # Notify the student about the application status change.
            _create_application_notification(
                cursor=cursor,
                user_id=student_id,
                title="Application Status Updated",
                message=(
                    f"Your application for '{internship_title}' "
                    f"has been updated from '{old_status}' "
                    f"to '{new_status}'."
                ),
                application_id=application_id
            )

            connection.commit()

            return True

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ==========================================
# APPLICATION STATUS HISTORY
# ==========================================

def get_application_history(application_id, recruiter_id):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    h.history_id,
                    h.old_status,
                    h.new_status,
                    h.remarks,
                    h.changed_at,
                    u.full_name
                FROM application_status_history h
                JOIN users u ON h.changed_by = u.user_id
                JOIN applications a ON h.application_id = a.application_id
                JOIN internships i ON a.internship_id = i.internship_id
                WHERE h.application_id = %s
                  AND i.created_by = %s
                ORDER BY h.changed_at DESC
                """,
                (application_id, recruiter_id)
            )

            rows = cursor.fetchall()

            return [
                {
                    "history_id": row[0],
                    "old_status": row[1],
                    "new_status": row[2],
                    "remarks": row[3],
                    "changed_at": row[4],
                    "changed_by": row[5]
                }
                for row in rows
            ]

    finally:
        connection.close()


# ==========================================
# SAVE INTERNSHIP
# ==========================================

def save_internship(student_id, internship_id):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM students WHERE student_id = %s",
                (student_id,)
            )
            if not cursor.fetchone():
                return "profile_not_found"

            cursor.execute(
                """
                SELECT 1
                FROM internships
                WHERE internship_id = %s
                  AND status = 'Open'
                  AND application_deadline >= CURRENT_DATE
                  AND available_positions > 0
                """,
                (internship_id,)
            )
            if not cursor.fetchone():
                return "internship_unavailable"

            cursor.execute(
                """
                INSERT INTO saved_internships (student_id, internship_id)
                VALUES (%s, %s)
                ON CONFLICT (student_id, internship_id) DO NOTHING
                RETURNING saved_id
                """,
                (student_id, internship_id)
            )

            result = cursor.fetchone()
            if not result:
                return "already_saved"

            connection.commit()
            return "saved"

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ==========================================
# VIEW SAVED INTERNSHIPS
# ==========================================

def get_saved_internships(student_id):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    i.internship_id,
                    i.title,
                    c.company_name,
                    i.work_mode,
                    i.location,
                    i.stipend,
                    si.saved_at
                FROM saved_internships si
                JOIN internships i ON si.internship_id = i.internship_id
                JOIN companies c ON i.company_id = c.company_id
                WHERE si.student_id = %s
                ORDER BY si.saved_at DESC
                """,
                (student_id,)
            )

            rows = cursor.fetchall()

            return [
                {
                    "internship_id": row[0],
                    "title": row[1],
                    "company_name": row[2],
                    "work_mode": row[3],
                    "location": row[4],
                    "stipend": float(row[5]),
                    "saved_at": row[6]
                }
                for row in rows
            ]

    finally:
        connection.close()


# ==========================================
# UPDATE STUDENT PREFERENCES
# ==========================================

def update_student_preferences(student_id, data):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO student_preferences (
                    student_id,
                    preferred_domain,
                    preferred_location,
                    preferred_work_mode,
                    minimum_stipend,
                    preferred_duration
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (student_id)
                DO UPDATE SET
                    preferred_domain = EXCLUDED.preferred_domain,
                    preferred_location = EXCLUDED.preferred_location,
                    preferred_work_mode = EXCLUDED.preferred_work_mode,
                    minimum_stipend = EXCLUDED.minimum_stipend,
                    preferred_duration = EXCLUDED.preferred_duration
                RETURNING preference_id
                """,
                (
                    student_id,
                    data.preferred_domain,
                    data.preferred_location,
                    data.preferred_work_mode,
                    data.minimum_stipend,
                    data.preferred_duration
                )
            )

            result = cursor.fetchone()

            connection.commit()

            return result is not None

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()