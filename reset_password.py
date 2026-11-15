
from database import get_connection
from auth import init_auth_table
from werkzeug.security import generate_password_hash
import getpass


def reset_password():
<<<<<<< Updated upstream
    print("\n===== Reset Password =====")
    print("1. Teacher")
    print("2. Admin")
    print("3. Student")

    user_type = input("Select account type (1, 2, or 3): ").strip()

    user_types = {
        "1": "teacher",
        "2": "admin",
        "3": "student"
    }

    if user_type not in user_types:
        print("Invalid account type!")
        return

    user_id = user_types[user_type]

    password = getpass.getpass("Enter new password: ")
    confirm_password = getpass.getpass("Confirm new password: ")

    if len(password) < 8:
        print("Password must contain at least 8 characters.")
        return

    if password != confirm_password:
        print("Passwords do not match!")
        return
=======
>>>>>>> Stashed changes

    init_auth_table()

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user_id, role
            FROM auth_users
            WHERE role IN ('teacher', 'student')
            ORDER BY role, user_id
        """)

        users = cursor.fetchall()

        if not users:
            print("No Teacher or Student accounts found!")
            return

        print("\nTeacher and Student Accounts:")

        for user in users:
            print(f"Login ID: {user[0]} | Role: {user[1].capitalize()}")

        user_id = input("\nEnter Teacher/Student Login ID: ").strip()

        cursor.execute("""
            SELECT user_id, role
            FROM auth_users
            WHERE user_id = ?
            AND role IN ('teacher', 'student')
        """, (user_id,))

        user = cursor.fetchone()

        if not user:
            print("Invalid Login ID! Admin accounts cannot be changed.")
            return

        password = getpass.getpass("Enter new password: ")
        confirm_password = getpass.getpass("Confirm new password: ")

        if len(password) < 8:
            print("Password must contain at least 8 characters.")
            return

        if password != confirm_password:
            print("Passwords do not match!")
            return

        password_hash = generate_password_hash(password)

        cursor.execute("""
            UPDATE auth_users
            SET password_hash = ?
            WHERE user_id = ?
            AND role IN ('teacher', 'student')
        """, (password_hash, user_id))

        conn.commit()

<<<<<<< Updated upstream
        print(f"{user_id.capitalize()} account password reset successfully!")
=======
        print(
            f"\n{user[1].capitalize()} password reset successfully!"
        )
>>>>>>> Stashed changes

    except Exception as e:
        conn.rollback()
        print("Error:", e)

    finally:
        conn.close()


if __name__ == "__main__":
    reset_password()
