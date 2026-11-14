
from database import get_connection
from auth import init_auth_table
from werkzeug.security import generate_password_hash
import getpass


def reset_password():
    print("\n===== Reset Password =====")
    print("1. Teacher")
    print("2. Student")

    user_type = input("Select account type (1 or 2): ").strip()

    if user_type == "1":
        user_id = "teacher"
    elif user_type == "2":
        user_id = "student"
    else:
        print("Invalid account type!")
        return

    password = getpass.getpass("Enter new password: ")
    confirm_password = getpass.getpass("Confirm new password: ")

    if len(password) < 8:
        print("Password must contain at least 8 characters.")
        return

    if password != confirm_password:
        print("Passwords do not match!")
        return

    init_auth_table()

    conn = get_connection()

    try:
        cursor = conn.cursor()
        password_hash = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO auth_users (user_id, password_hash)
            VALUES (?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET password_hash = excluded.password_hash
        """, (user_id, password_hash))

        conn.commit()

        print(f"{user_type_name(user_id)} account password reset successfully!")

    except Exception as e:
        conn.rollback()
        print("Error:", e)

    finally:
        conn.close()


def user_type_name(user_id):
    return "Teacher" if user_id == "teacher" else "Student"


if __name__ == "__main__":
    reset_password()
