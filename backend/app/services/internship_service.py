from app.db.postgres import get_postgres_connection




# ==========================================
# AUTOMATIC INTERNSHIP EMBEDDING REFRESH
# ==========================================

def refresh_internship_embedding_safely(internship_id):
    """Embedding-based AI matching is disabled in this build.

    Keep this compatibility function because create/update flows call it.
    It intentionally performs no network or model operations.
    """
    return {
        "status": "disabled",
        "internship_id": internship_id,
        "message": "AI recommendation embeddings are disabled."
    }

# ==========================================
# CREATE INTERNSHIP
# ==========================================

def create_internship(recruiter_id, data):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT company_id
                FROM recruiters
                WHERE recruiter_id = %s
                """,
                (recruiter_id,)
            )

            recruiter = cursor.fetchone()

            if not recruiter:
                return None

            company_id = recruiter[0]

            cursor.execute(
                """
                INSERT INTO internships (
                    company_id,
                    created_by,
                    title,
                    description,
                    work_mode,
                    location,
                    stipend,
                    duration_months,
                    available_positions,
                    minimum_cgpa,
                    minimum_year,
                    application_deadline,
                    status
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING internship_id
                """,
                (
                    company_id,
                    recruiter_id,
                    data.title,
                    data.description,
                    data.work_mode,
                    data.location,
                    data.stipend,
                    data.duration_months,
                    data.available_positions,
                    data.minimum_cgpa,
                    data.minimum_year,
                    data.application_deadline,
                    data.status
                )
            )

            result = cursor.fetchone()

            connection.commit()

            refresh_internship_embedding_safely(result[0])

            return result[0]

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ==========================================
# VIEW ALL OPEN INTERNSHIPS
# ==========================================

def get_all_internships():

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
                    i.available_positions,
                    i.minimum_cgpa,
                    i.minimum_year,
                    i.application_deadline,
                    i.status
                FROM internships i
                JOIN companies c
                    ON i.company_id = c.company_id
                WHERE i.status = 'Open'
                ORDER BY i.created_at DESC
                """
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
                    "available_positions": row[8],
                    "minimum_cgpa": float(row[9]),
                    "minimum_year": row[10],
                    "application_deadline": row[11],
                    "status": row[12]
                }
                for row in rows
            ]

    finally:
        connection.close()


def get_recruiter_internships(recruiter_id):
    """Return all internships belonging to the logged-in recruiter."""

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
                    i.available_positions,
                    i.minimum_cgpa,
                    i.minimum_year,
                    i.application_deadline,
                    i.status
                FROM internships i
                JOIN companies c
                    ON i.company_id = c.company_id
                WHERE i.created_by = %s
                ORDER BY i.created_at DESC
                """,
                (recruiter_id,)
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
                    "available_positions": row[8],
                    "minimum_cgpa": float(row[9]),
                    "minimum_year": row[10],
                    "application_deadline": row[11],
                    "status": row[12]
                }
                for row in rows
            ]

    finally:
        connection.close()


# ==========================================
# VIEW SINGLE INTERNSHIP
# ==========================================

def get_internship(internship_id):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    i.*,
                    c.company_name
                FROM internships i
                JOIN companies c
                    ON i.company_id = c.company_id
                WHERE i.internship_id = %s
                """,
                (internship_id,)
            )

            row = cursor.fetchone()

            if not row:
                return None

            return {
                "internship_id": row[0],
                "company_id": row[1],
                "created_by": row[2],
                "title": row[3],
                "description": row[4],
                "work_mode": row[5],
                "location": row[6],
                "stipend": float(row[7]),
                "duration_months": row[8],
                "available_positions": row[9],
                "minimum_cgpa": float(row[10]),
                "minimum_year": row[11],
                "application_deadline": row[12],
                "status": row[13],
                "created_at": row[14],
                "company_name": row[15]
            }

    finally:
        connection.close()


# ==========================================
# UPDATE INTERNSHIP
# ==========================================

def update_internship(recruiter_id, internship_id, data):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE internships
                SET
                    title = %s,
                    description = %s,
                    work_mode = %s,
                    location = %s,
                    stipend = %s,
                    duration_months = %s,
                    available_positions = %s,
                    minimum_cgpa = %s,
                    minimum_year = %s,
                    application_deadline = %s,
                    status = %s
                WHERE internship_id = %s
                AND created_by = %s
                RETURNING internship_id
                """,
                (
                    data.title,
                    data.description,
                    data.work_mode,
                    data.location,
                    data.stipend,
                    data.duration_months,
                    data.available_positions,
                    data.minimum_cgpa,
                    data.minimum_year,
                    data.application_deadline,
                    data.status,
                    internship_id,
                    recruiter_id
                )
            )

            result = cursor.fetchone()

            connection.commit()

            if result:
                refresh_internship_embedding_safely(internship_id)

            return result is not None

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ==========================================
# DELETE INTERNSHIP
# ==========================================

def delete_internship(recruiter_id, internship_id):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM internships
                WHERE internship_id = %s
                AND created_by = %s
                RETURNING internship_id
                """,
                (internship_id, recruiter_id)
            )

            result = cursor.fetchone()

            connection.commit()

            return result is not None

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ==========================================
# ADD INTERNSHIP SKILLS
# ==========================================

def add_internship_skill(internship_id, data):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO internship_skills (
                    internship_id,
                    skill_id,
                    requirement_type,
                    minimum_proficiency,
                    importance_weight
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (internship_id, skill_id)
                DO UPDATE SET
                    requirement_type = EXCLUDED.requirement_type,
                    minimum_proficiency = EXCLUDED.minimum_proficiency,
                    importance_weight = EXCLUDED.importance_weight
                RETURNING skill_id
                """,
                (
                    internship_id,
                    data.skill_id,
                    data.requirement_type,
                    data.minimum_proficiency,
                    data.importance_weight
                )
            )

            result = cursor.fetchone()

            connection.commit()

            if result:
                refresh_internship_embedding_safely(internship_id)

            return result is not None

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ==========================================
# VIEW INTERNSHIP SKILLS
# ==========================================

def get_internship_skills(internship_id):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    s.skill_id,
                    s.skill_name,
                    s.skill_category,
                    isk.requirement_type,
                    isk.minimum_proficiency,
                    isk.importance_weight
                FROM internship_skills isk
                JOIN skills s
                    ON isk.skill_id = s.skill_id
                WHERE isk.internship_id = %s
                ORDER BY isk.importance_weight DESC
                """,
                (internship_id,)
            )

            rows = cursor.fetchall()

            return [
                {
                    "skill_id": row[0],
                    "skill_name": row[1],
                    "skill_category": row[2],
                    "requirement_type": row[3],
                    "minimum_proficiency": row[4],
                    "importance_weight": float(row[5])
                }
                for row in rows
            ]

    finally:
        connection.close()
