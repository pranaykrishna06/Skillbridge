from app.db.postgres import get_postgres_connection
from app.core.security import hash_password, verify_password, create_access_token


def register_user(full_name, email, password, role):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT role_id FROM roles WHERE LOWER(role_name) = LOWER(%s)",
                (role,)
            )

            role_result = cursor.fetchone()

            if not role_result:
                return None

            role_id = role_result[0]

            cursor.execute(
                "SELECT user_id FROM users WHERE email = %s",
                (email,)
            )

            if cursor.fetchone():
                return None

            hashed_password = hash_password(password)

            cursor.execute(
                """
                INSERT INTO users
                (role_id, full_name, email, password_hash)
                VALUES (%s, %s, %s, %s)
                RETURNING user_id, full_name, email
                """,
                (role_id, full_name, email, hashed_password)
            )

            user = cursor.fetchone()

            connection.commit()

            return {
                "user_id": user[0],
                "full_name": user[1],
                "email": user[2],
                "role": role
            }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def login_user(email, password):

    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT u.user_id, u.full_name, u.email,
                       u.password_hash, r.role_name
                FROM users u
                JOIN roles r ON u.role_id = r.role_id
                WHERE u.email = %s AND u.is_active = TRUE
                """,
                (email,)
            )

            user = cursor.fetchone()

            if not user:
                return None

            if not verify_password(password, user[3]):
                return None

            token = create_access_token({
                "sub": str(user[0]),
                "role": user[4]
            })

            return {
                "access_token": token,
                "token_type": "bearer"
            }

    finally:
        connection.close()
