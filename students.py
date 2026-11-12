from database import get_connection

def add_student():
    print("\n--- Add New Student ---")
    name = input("Enter student name: ")
    roll_number = input("Enter roll number: ")
    course = input("Enter course: ")
    try:
        semester = int(input("Enter semester: "))
        if not name.strip() or not roll_number.strip() or not course.strip():
            print("All fields are required.")
            return
        if semester < 1:
            print("Semester must be at least 1.")
            return
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO students (name, roll_number, course, semester)
            VALUES (?, ?, ?, ?)
        """, (name, roll_number, course, semester))
        conn.commit()
        print("Student added successfully!")
    except ValueError:
        print("Semester must be a valid number.")
    except Exception as e:
        print("Error:", e)
    finally:
        if 'conn' in locals():
            conn.close()


def view_students():
    print("\n--- Student Records ---")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    if not students:
        print("No students found.")
    else:
        for student in students:
            print(student)
    conn.close()


def search_student():
    roll_number = input("Enter roll number to search: ")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM students WHERE roll_number = ?",
        (roll_number,)
    )
    student = cursor.fetchone()
    if student:
        print("Student found:", student)
    else:
        print("Student not found.")
    conn.close()


def delete_student():
    roll_number = input("Enter roll number to delete: ")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM students WHERE roll_number = ?",
        (roll_number,)
    )
    conn.commit()
    if cursor.rowcount > 0:
        print("Student deleted successfully!")
    else:
        print("Student not found.")
    conn.close()


def update_student():
    print("\n--- Update Student Details ---")
    roll_number = input("Enter roll number of student: ")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM students WHERE roll_number = ?",
        (roll_number,)
    )
    student = cursor.fetchone()
    if not student:
        print("Student not found.")
        conn.close()
        return
    print("\nCurrent Details:")
    print("Name:", student[1])
    print("Roll Number:", student[2])
    print("Course:", student[3])
    print("Semester:", student[4])
    name = input("Enter new name: ")
    course = input("Enter new course: ")
    try:
        semester = int(input("Enter new semester: "))
        if not name.strip() or not course.strip() or semester < 1:
            print("Invalid details. All fields are required.")
            conn.close()
            return
        cursor.execute("""
            UPDATE students
            SET name = ?, course = ?, semester = ?
            WHERE roll_number = ?
        """, (name, course, semester, roll_number))
        conn.commit()
        print("Student updated successfully!")
    except ValueError:
        print("Semester must be a valid number.")
    finally:
        conn.close()
