from app.db.postgres import get_postgres_connection


# ==========================================
# COMPANY REGISTRATION
# ==========================================

def create_company(recruiter_id, data):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT recruiter_id
                FROM recruiters
                WHERE recruiter_id = %s
                """,
                (recruiter_id,)
            )

            if cursor.fetchone():
                return None

            cursor.execute(
                """
                INSERT INTO companies (
                    company_name,
                    registration_number,
                    industry,
                    description,
                    website,
                    location
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING company_id
                """,
                (
                    data.company_name,
                    data.registration_number,
                    data.industry,
                    data.description,
                    data.website,
                    data.location
                )
            )

            company_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO recruiters (
                    recruiter_id,
                    company_id,
                    designation
                )
                VALUES (%s, %s, %s)
                """,
                (
                    recruiter_id,
                    company_id,
                    data.designation
                )
            )

            connection.commit()

            return company_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ==========================================
# VIEW COMPANY
# ==========================================

def get_company(recruiter_id):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    c.company_id,
                    c.company_name,
                    c.registration_number,
                    c.industry,
                    c.description,
                    c.website,
                    c.location,
                    c.verification_status,
                    r.designation
                FROM companies c
                JOIN recruiters r
                    ON c.company_id = r.company_id
                WHERE r.recruiter_id = %s
                """,
                (recruiter_id,)
            )

            row = cursor.fetchone()

            if not row:
                return None

            return {
                "company_id": row[0],
                "company_name": row[1],
                "registration_number": row[2],
                "industry": row[3],
                "description": row[4],
                "website": row[5],
                "location": row[6],
                "verification_status": row[7],
                "designation": row[8]
            }

    finally:
        connection.close()


# ==========================================
# UPDATE COMPANY
# ==========================================

def update_company(recruiter_id, data):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE companies
                SET
                    company_name = %s,
                    industry = %s,
                    description = %s,
                    website = %s,
                    location = %s
                WHERE company_id = (
                    SELECT company_id
                    FROM recruiters
                    WHERE recruiter_id = %s
                )
                RETURNING company_id
                """,
                (
                    data.company_name,
                    data.industry,
                    data.description,
                    data.website,
                    data.location,
                    recruiter_id
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


# ==========================================
# VIEW RECRUITER PROFILE
# ==========================================

def get_recruiter_profile(recruiter_id):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    u.user_id,
                    u.full_name,
                    u.email,
                    u.phone,
                    r.designation,
                    r.verification_status,
                    c.company_id,
                    c.company_name
                FROM recruiters r
                JOIN users u
                    ON r.recruiter_id = u.user_id
                JOIN companies c
                    ON r.company_id = c.company_id
                WHERE r.recruiter_id = %s
                """,
                (recruiter_id,)
            )

            row = cursor.fetchone()

            if not row:
                return None

            return {
                "recruiter_id": row[0],
                "full_name": row[1],
                "email": row[2],
                "phone": row[3],
                "designation": row[4],
                "verification_status": row[5],
                "company_id": row[6],
                "company_name": row[7]
            }

    finally:
        connection.close()


# ==========================================
# UPDATE RECRUITER PROFILE
# ==========================================

def update_recruiter_profile(recruiter_id, designation):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE recruiters
                SET designation = %s
                WHERE recruiter_id = %s
                RETURNING recruiter_id
                """,
                (designation, recruiter_id)
            )

            result = cursor.fetchone()

            connection.commit()

            return result is not None

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
