from database import get_connection
import sqlite3

def add_student_record(name, roll_number, course, semester):
    name = name.strip()
    roll_number = roll_number.strip()
    course = course.strip()
    if not name or not roll_number or not course:
        return False, "All fields are required."
    try:
        semester = int(semester)
        if semester < 1:
            return False, "Semester must be at least 1."
    except (ValueError, TypeError):
        return False, "Semester must be a valid number."
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO students (name, roll_number, course, semester)
            VALUES (?, ?, ?, ?)
        """, (name, roll_number, course, semester))
        conn.commit()
        return True, "Student added successfully!"
    except sqlite3.IntegrityError:
        return False, "This roll number already exists."
    finally:
        conn.close()

def get_all_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT student_id, name, roll_number, course, semester
        FROM students
        ORDER BY name
    """)
    students = cursor.fetchall()
    conn.close()
    return students

def search_student_record(query):
    query = query.strip()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT student_id, name, roll_number, course, semester
        FROM students
        WHERE name LIKE ? OR roll_number LIKE ?
        ORDER BY name
    """, (f"%{query}%", f"%{query}%"))
    students = cursor.fetchall()
    conn.close()
    return students

def delete_student_record(roll_number):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM students WHERE roll_number = ?",
            (roll_number.strip(),)
        )
        if cursor.rowcount == 0:
            return False, "Student not found."
        conn.commit()
        return True, "Student deleted successfully!"
    except sqlite3.IntegrityError:
        return False, "Cannot delete student because attendance records are linked to this student."
    finally:
        conn.close()

def update_student_record(roll_number, name, course, semester):
    name = name.strip()
    course = course.strip()
    if not name or not course:
        return False, "All fields are required."
    try:
        semester = int(semester)
        if semester < 1:
            return False, "Semester must be at least 1."
    except (ValueError, TypeError):
        return False, "Semester must be a valid number."
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE students
            SET name = ?, course = ?, semester = ?
            WHERE roll_number = ?
        """, (name, course, semester, roll_number.strip()))
        if cursor.rowcount == 0:
            return False, "Student not found."
        conn.commit()
        return True, "Student updated successfully!"
    finally:
        conn.close()

def add_student():
    print("\n--- Add New Student ---")
    name = input("Enter student name: ")
    roll_number = input("Enter roll number: ")
    course = input("Enter course: ")
    semester = input("Enter semester: ")
    success, message = add_student_record(
        name, roll_number, course, semester
    )
    print(message)

def view_students():
    print("\n--- Student Records ---")
    students = get_all_students()
    if not students:
        print("No students found.")
        return
    for student in students:
        print(student)

def search_student():
    roll_number = input("Enter roll number to search: ")
    students = search_student_record(roll_number)
    if students:
        for student in students:
            print("Student found:", student)
    else:
        print("Student not found.")

def delete_student():
    roll_number = input("Enter roll number to delete: ")
    success, message = delete_student_record(roll_number)
    print(message)

def update_student():
    print("\n--- Update Student Details ---")
    roll_number = input("Enter roll number of student: ")
    name = input("Enter new name: ")
    course = input("Enter new course: ")
    semester = input("Enter new semester: ")
    success, message = update_student_record(
        roll_number, name, course, semester
    )
    print(message)
