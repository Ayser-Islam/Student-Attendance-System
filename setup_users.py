
from auth import init_auth_table, create_auth_user
import getpass

init_auth_table()

for user_id in ["1", "2", "3"]:
    print(f"\nCreate password for Login ID: {user_id}")

    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Confirm password: ")

    if password != confirm_password:
        print("Passwords do not match. Try again.")
        continue

    if len(password) < 8:
        print("Password must contain at least 8 characters.")
        continue

    success, message = create_auth_user(user_id, password)
    print(message)

print("\nAccount setup completed!")

