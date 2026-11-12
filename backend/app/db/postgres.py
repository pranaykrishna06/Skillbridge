import psycopg

from app.core.config import settings


def get_postgres_connection():
    connection = psycopg.connect(
        settings.DATABASE_URL
    )
    return connection


def check_postgres_connection():
    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            result = cursor.fetchone()
            return result[0]

    finally:
        connection.close()