
from database import get_connection, DATABASE_PATH

print("Database being checked:", DATABASE_PATH)

conn = get_connection()

try:
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(auth_users)")
    columns = [column[1] for column in cursor.fetchall()]

    print("\nDatabase columns:", columns)

    if not columns:
        print("auth_users table does not exist!")
    else:
        cursor.execute("SELECT * FROM auth_users")
        users = cursor.fetchall()

        print("\nAll accounts:")

        if not users:
            print("No accounts found!")
        else:
            for user in users:
                print(user)

finally:
    conn.close()

