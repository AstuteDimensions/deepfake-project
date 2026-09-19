import os
import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

class DatabaseUnavailableError(Exception):
    pass

def get_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

    except mysql.connector.Error as e:
        raise DatabaseUnavailableError(
            "Database is temporarily unavailable."
        ) from e
        
def log_activity(user_id, action):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        query = """
        INSERT INTO activity_log (user_id, action)
        VALUES (%s, %s)
        """

        cursor.execute(query, (user_id, action))
        connection.commit()

    finally:
        cursor.close()
        connection.close()

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

        user_id = cursor.lastrowid
        log_activity(user_id, "Account created")

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
def get_user_id_by_login(login):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
        SELECT user_id
        FROM users
        WHERE email = %s OR username = %s
        """

        cursor.execute(query, (login, login))
        user = cursor.fetchone()

        if user:
            return user["user_id"]

        return None

    finally:
        cursor.close()
        connection.close()


def update_user_profile(user_id, username, email):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        query = """
        UPDATE users
        SET username = %s, email = %s
        WHERE user_id = %s
        """

        cursor.execute(
            query,
            (username, email, user_id)
        )

        connection.commit()

        return True, "Profile updated successfully."

    except mysql.connector.IntegrityError:
        return False, "An account with this email already exists."

    finally:
        cursor.close()
        connection.close()


def change_user_password(user_id, current_password, new_password):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT password_hash
            FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:
            return False, "User not found."

        if not check_password_hash(
            user["password_hash"],
            current_password
        ):
            return False, "Current password is incorrect."

        new_hash = generate_password_hash(
            new_password
        )

        cursor.execute(
            """
            UPDATE users
            SET password_hash = %s
            WHERE user_id = %s
            """,
            (new_hash, user_id)
        )

        connection.commit()

        return True, "Password changed successfully."

    finally:
        cursor.close()
        connection.close()

def get_user_id_by_login(login):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
        SELECT user_id
        FROM users
        WHERE email = %s OR username = %s
        """

        cursor.execute(query, (login, login))
        user = cursor.fetchone()

        if user:
            return user["user_id"]

        return None

    finally:
        cursor.close()
        connection.close()


def update_user_profile(user_id, username, email):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        query = """
        UPDATE users
        SET username = %s, email = %s
        WHERE user_id = %s
        """

        cursor.execute(
            query,
            (username, email, user_id)
        )

        connection.commit()

        return True, "Profile updated successfully."

    except mysql.connector.IntegrityError:
        return False, "An account with this email already exists."

    finally:
        cursor.close()
        connection.close()


def change_user_password(user_id, current_password, new_password):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT password_hash
            FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:
            return False, "User not found."

        if not check_password_hash(
            user["password_hash"],
            current_password
        ):
            return False, "Current password is incorrect."

        new_hash = generate_password_hash(
            new_password
        )

        cursor.execute(
            """
            UPDATE users
            SET password_hash = %s
            WHERE user_id = %s
            """,
            (new_hash, user_id)
        )

        connection.commit()

        return True, "Password changed successfully."

    finally:
        cursor.close()
        connection.close()