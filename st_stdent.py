

from auth import init_auth_table, create_auth_user
from database import initialize_database, get_connection
from getpass import getpass


def setup_students():

    initialize_database()
    init_auth_table()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT student_id, roll_number, name
        FROM students
        ORDER BY roll_number
    """)

    students = cursor.fetchall()
    conn.close()

    if not students:
        print("No student records found!")
        print("Please add students first.")
        return

    print("\n===== STUDENT ACCOUNT SETUP =====")

    for student in students:

        student_id = student[0]
        roll_number = str(student[1])
        name = student[2]

        print("\n-----------------------------")
        print("Student:", name)
        print("Roll Number:", roll_number)

        success, message = create_auth_user(
            roll_number,
            getpass("Enter student password: "),
            "student",
            student_id
        )

        print(message)

    print("\nStudent account setup completed!")


if __name__ == "__main__":
    setup_students()
