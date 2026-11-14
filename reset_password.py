
from database import get_connection
from auth import init_auth_table
from werkzeug.security import generate_password_hash
import getpass


def reset_password():
    user_id = input("Enter Login ID (1, 2, or 3): ").strip()

    if user_id not in ["1", "2", "3"]:
        print("Invalid Login ID!")
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

        print(f"Account {user_id} created or password reset successfully!")

    except Exception as e:
        conn.rollback()
        print("Error:", e)

    finally:
        conn.close()


if __name__ == "__main__":
    reset_password()
