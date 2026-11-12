from app.db.postgres import get_postgres_connection
from app.services.embedding_service import generate_embedding


def find_similar_internships(student_id: int, limit: int = 10):
    """
    Find internships semantically similar to a student's profile.
    """

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT embedding
                FROM student_embeddings
                WHERE student_id = %s
                """,
                (student_id,)
            )

            result = cursor.fetchone()

            if not result:
                raise ValueError(
                    "Student embedding not found. Generate it first."
                )

            student_embedding = result[0]

            cursor.execute(
                """
                SELECT
                    ie.internship_id,
                    i.title,
                    c.company_name,
                    i.description,
                    1 - (
                        ie.embedding <=> %s::vector
                    ) AS similarity
                FROM internship_embeddings ie
                JOIN internships i
                    ON i.internship_id = ie.internship_id
                JOIN companies c
                    ON c.company_id = i.company_id
                WHERE i.status = 'Open'
                  AND i.application_deadline >= CURRENT_DATE
                ORDER BY ie.embedding <=> %s::vector
                LIMIT %s
                """,
                (
                    str(student_embedding),
                    str(student_embedding),
                    limit
                )
            )

            results = cursor.fetchall()

            return [
                {
                    "internship_id": row[0],
                    "title": row[1],
                    "company": row[2],
                    "description": row[3],
                    "similarity_percentage": round(
                        float(row[4]) * 100, 2
                    )
                }
                for row in results
            ]

    finally:
        connection.close()


def search_internships_by_text(query: str, limit: int = 10):
    """
    Search internships using a natural-language query.
    """

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    query_embedding = generate_embedding(query)

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    ie.internship_id,
                    i.title,
                    c.company_name,
                    1 - (
                        ie.embedding <=> %s::vector
                    ) AS similarity
                FROM internship_embeddings ie
                JOIN internships i
                    ON i.internship_id = ie.internship_id
                JOIN companies c
                    ON c.company_id = i.company_id
                WHERE i.status = 'Open'
                  AND i.application_deadline >= CURRENT_DATE
                ORDER BY ie.embedding <=> %s::vector
                LIMIT %s
                """,
                (
                    str(query_embedding),
                    str(query_embedding),
                    limit
                )
            )

            results = cursor.fetchall()

            return [
                {
                    "internship_id": row[0],
                    "title": row[1],
                    "company": row[2],
                    "similarity_percentage": round(
                        float(row[3]) * 100, 2
                    )
                }
                for row in results
            ]

    finally:
        connection.close()
