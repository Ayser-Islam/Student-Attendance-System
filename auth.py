
from database import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import session, redirect, url_for, flash


def init_auth_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_users (
            user_id TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def create_auth_user(user_id, password):
    if not user_id or not password:
        return False, "User ID and password are required."

    conn = get_connection()

    try:
        cursor = conn.cursor()

        password_hash = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO auth_users (user_id, password_hash)
            VALUES (?, ?)
        """, (user_id, password_hash))

        conn.commit()
        return True, "Account created successfully!"

    except Exception as e:
        return False, str(e)

    finally:
        conn.close()


def authenticate_user(user_id, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, password_hash
        FROM auth_users
        WHERE user_id = ?
    """, (user_id,))

    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[1], password):
        return True, user[0]

    return False, None


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "error")
            return redirect(url_for("login"))

        return func(*args, **kwargs)

    return wrapper


