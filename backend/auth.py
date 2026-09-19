import os
import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


def register_user(username, email, password):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        password_hash = generate_password_hash(password)

        query = """
        INSERT INTO users (username, email, password_hash, auth_provider)
        VALUES (%s, %s, %s, 'local')
        """

        cursor.execute(query, (username, email, password_hash))
        connection.commit()

        return True, "Account created successfully."

    except mysql.connector.IntegrityError:
        return False, "An account with this email already exists."

    finally:
        cursor.close()
        connection.close()


def authenticate_user(email, password):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
        SELECT user_id, username, email, password_hash
        FROM users
        WHERE email = %s OR username = %s
        """

        cursor.execute(query, (email, email))
        user = cursor.fetchone()

        if not user:
            return None

        if not check_password_hash(user["password_hash"], password):
            return None

        return user

    finally:
        cursor.close()
        connection.close()