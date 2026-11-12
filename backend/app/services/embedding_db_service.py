from app.db.postgres import get_postgres_connection
from app.services.embedding_service import (
    generate_embedding,
    MODEL_NAME
)


def build_student_text(student_id: int):
    """
    Retrieve student profile, skills and projects
    and construct text for semantic embedding.
    """

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    u.full_name,
                    s.department,
                    s.year_of_study,
                    s.cgpa,
                    s.graduation_year,
                    s.bio
                FROM students s
                JOIN users u ON u.user_id = s.student_id
                WHERE s.student_id = %s
                """,
                (student_id,)
            )

            student = cursor.fetchone()

            if not student:
                raise ValueError(
                    f"Student {student_id} not found."
                )

            name, department, year, cgpa, graduation, bio = student

            cursor.execute(
                """
                SELECT sk.skill_name,
                       ss.proficiency_level,
                       ss.years_experience
                FROM student_skills ss
                JOIN skills sk ON sk.skill_id = ss.skill_id
                WHERE ss.student_id = %s
                """,
                (student_id,)
            )

            skills = cursor.fetchall()

            cursor.execute(
                """
                SELECT project_title, project_description
                FROM student_projects
                WHERE student_id = %s
                """,
                (student_id,)
            )

            projects = cursor.fetchall()

        skill_text = ", ".join(
            f"{name} ({level}, {experience} years experience)"
            for name, level, experience in skills
        )

        project_text = " ".join(
            f"{title}: {description}"
            for title, description in projects
        )

        source_text = f"""
        Student: {name}.
        Department: {department}.
        Year of study: {year}.
        CGPA: {cgpa}.
        Graduation year: {graduation}.
        Profile: {bio or 'Not provided'}.
        Skills: {skill_text or 'Not provided'}.
        Projects: {project_text or 'Not provided'}.
        """

        return " ".join(source_text.split())

    finally:
        connection.close()


def build_internship_text(internship_id: int):
    """
    Retrieve internship details and required skills
    and construct text for semantic embedding.
    """

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    i.title,
                    i.description,
                    i.work_mode,
                    i.location,
                    i.stipend,
                    i.duration_months,
                    i.minimum_cgpa,
                    i.minimum_year,
                    c.company_name,
                    c.industry
                FROM internships i
                JOIN companies c
                    ON c.company_id = i.company_id
                WHERE i.internship_id = %s
                """,
                (internship_id,)
            )

            internship = cursor.fetchone()

            if not internship:
                raise ValueError(
                    f"Internship {internship_id} not found."
                )

            (
                title,
                description,
                work_mode,
                location,
                stipend,
                duration,
                minimum_cgpa,
                minimum_year,
                company,
                industry
            ) = internship

            cursor.execute(
                """
                SELECT
                    sk.skill_name,
                    isk.requirement_type,
                    isk.minimum_proficiency
                FROM internship_skills isk
                JOIN skills sk
                    ON sk.skill_id = isk.skill_id
                WHERE isk.internship_id = %s
                """,
                (internship_id,)
            )

            skills = cursor.fetchall()

        skill_text = ", ".join(
            f"{name} ({requirement}, minimum {proficiency})"
            for name, requirement, proficiency in skills
        )

        source_text = f"""
        Internship: {title}.
        Company: {company}.
        Industry: {industry}.
        Description: {description}.
        Work mode: {work_mode}.
        Location: {location}.
        Stipend: {stipend}.
        Duration: {duration} months.
        Minimum CGPA: {minimum_cgpa}.
        Minimum study year: {minimum_year}.
        Required skills: {skill_text or 'Not specified'}.
        """

        return " ".join(source_text.split())

    finally:
        connection.close()


def generate_student_embedding(student_id: int):
    """
    Generate and store a student's embedding.
    """

    source_text = build_student_text(student_id)
    embedding = generate_embedding(source_text)

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO student_embeddings
                (
                    student_id,
                    source_text,
                    embedding,
                    embedding_model
                )
                VALUES (%s, %s, %s::vector, %s)

                ON CONFLICT (student_id)
                DO UPDATE SET
                    source_text = EXCLUDED.source_text,
                    embedding = EXCLUDED.embedding,
                    embedding_model = EXCLUDED.embedding_model,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    student_id,
                    source_text,
                    str(embedding),
                    MODEL_NAME
                )
            )

        connection.commit()

        return {
            "student_id": student_id,
            "dimensions": len(embedding),
            "status": "stored"
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def generate_internship_embedding(internship_id: int):
    """
    Generate and store an internship embedding.
    """

    source_text = build_internship_text(internship_id)
    embedding = generate_embedding(source_text)

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO internship_embeddings
                (
                    internship_id,
                    source_text,
                    embedding,
                    embedding_model
                )
                VALUES (%s, %s, %s::vector, %s)

                ON CONFLICT (internship_id)
                DO UPDATE SET
                    source_text = EXCLUDED.source_text,
                    embedding = EXCLUDED.embedding,
                    embedding_model = EXCLUDED.embedding_model,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    internship_id,
                    source_text,
                    str(embedding),
                    MODEL_NAME
                )
            )

        connection.commit()

        return {
            "internship_id": internship_id,
            "dimensions": len(embedding),
            "status": "stored"
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
