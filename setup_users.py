
from auth import init_auth_table, create_auth_user
from database import initialize_database, get_connection
from getpass import getpass


def setup_admin():

    initialize_database()
    init_auth_table()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id
        FROM auth_users
        WHERE role = 'admin'
        LIMIT 1
    """)

    existing_admin = cursor.fetchone()
    conn.close()

    if existing_admin:
        print("Admin account already exists!")
        print("Login ID:", existing_admin[0])
        return

    print("\n===== CREATE ADMIN ACCOUNT =====")

    user_id = input("Enter Admin Login ID: ").strip()

    if not user_id:
        print("Login ID cannot be empty.")
        return

    while True:
        password = getpass("Enter Admin Password: ")
        confirm_password = getpass("Confirm Admin Password: ")

        if password != confirm_password:
            print("Passwords do not match. Try again.")
            continue

        if len(password) < 8:
            print("Password must contain at least 8 characters.")
            continue

        break

    success, message = create_auth_user(
        user_id,
        password,
        "admin"
    )

    print(message)

    if success:
        print("\nAdmin account setup completed!")
        print("You can now log in to the Flask application.")


if __name__ == "__main__":
    setup_admin()
