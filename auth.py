
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
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'teacher',
            student_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)

    cursor.execute("PRAGMA table_info(auth_users)")
    columns = [column[1] for column in cursor.fetchall()]

    if "role" not in columns:
        cursor.execute("""
            ALTER TABLE auth_users
            ADD COLUMN role TEXT NOT NULL DEFAULT 'teacher'
        """)

    if "student_id" not in columns:
        cursor.execute("""
            ALTER TABLE auth_users
            ADD COLUMN student_id INTEGER
        """)

    if "created_at" not in columns:
        cursor.execute("""
            ALTER TABLE auth_users
            ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        """)

    if "is_active" not in columns:
        cursor.execute("""
            ALTER TABLE auth_users
            ADD COLUMN is_active INTEGER DEFAULT 1
        """)

    conn.commit()
    conn.close()


def create_auth_user(user_id, password, role, student_id=None):
    if not user_id or not password:
        return False, "User ID and password are required."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    if role not in ("admin", "teacher", "student"):
        return False, "Invalid user role."

    if role == "student" and student_id is None:
        return False, "Student record is required."

    if role != "student" and student_id is not None:
        return False, "Only student accounts can have a student record."

    conn = get_connection()

    try:
        cursor = conn.cursor()

        if role == "student":
            cursor.execute(
                "SELECT student_id FROM students WHERE student_id = ?",
                (student_id,)
            )

            if cursor.fetchone() is None:
                return False, "Student record does not exist."

            cursor.execute("""
                SELECT user_id FROM auth_users
                WHERE student_id = ?
            """, (student_id,))

            if cursor.fetchone():
                return False, "This student already has an account."

        password_hash = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO auth_users
            (user_id, password_hash, role, student_id)
            VALUES (?, ?, ?, ?)
        """, (user_id, password_hash, role, student_id))

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
        SELECT user_id, password_hash, role, student_id, is_active
        FROM auth_users
        WHERE user_id = ?
    """, (user_id,))

    user = cursor.fetchone()
    conn.close()

    if user and user[4] == 1 and check_password_hash(user[1], password):
        return True, {
            "user_id": user[0],
            "role": user[2],
            "student_id": user[3]
        }

    return False, None


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "error")
            return redirect(url_for("login"))

        return func(*args, **kwargs)

    return wrapper


def role_required(*allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                flash("Please login first.", "error")
                return redirect(url_for("login"))

            if session.get("role") not in allowed_roles:
                flash("You are not authorized to access this page.", "error")
                return redirect(url_for("home"))

            return func(*args, **kwargs)

        return wrapper

    return decorator
