from database import get_connection
from datetime import date
import sqlite3

def mark_attendance_record(roll_number, attendance_date, attendance_status):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT student_id FROM students WHERE roll_number = ?",
            (roll_number,)
        )
        student = cursor.fetchone()
        if not student:
            return False, "Student not found!"
        if attendance_status not in ["Present", "Absent", "Late"]:
            return False, "Invalid attendance status!"
        if not attendance_date:
            attendance_date = date.today().isoformat()
        parsed_date = date.fromisoformat(attendance_date)
        if parsed_date.isoformat() != attendance_date:
            return False, "Use date format YYYY-MM-DD."
        cursor.execute("""
            INSERT INTO attendance (student_id, date, status)
            VALUES (?, ?, ?)
        """, (student[0], attendance_date, attendance_status))
        conn.commit()
        return True, "Attendance marked successfully!"
    except ValueError:
        return False, "Invalid date!"
    except sqlite3.IntegrityError:
        return False, "Attendance already marked for this student on this date."
    finally:
        conn.close()

def get_all_attendance():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.attendance_id, s.name, s.roll_number, a.date, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        ORDER BY a.date DESC
    """)
    records = cursor.fetchall()
    conn.close()
    return records

def get_attendance_by_date(selected_date):
    try:
        date.fromisoformat(selected_date)
    except ValueError:
        return []

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.attendance_id, s.name, s.roll_number, a.date, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        WHERE a.date = ?
        ORDER BY a.date DESC
    """, (selected_date,))

    records = cursor.fetchall()
    conn.close()
    return records

def get_student_attendance(roll_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT student_id, name
        FROM students
        WHERE roll_number = ?
    """, (roll_number,))
    student = cursor.fetchone()
    if not student:
        conn.close()
        return None, []
    cursor.execute("""
        SELECT date, status
        FROM attendance
        WHERE student_id = ?
        ORDER BY date DESC
    """, (student[0],))
    records = cursor.fetchall()
    conn.close()
    return student, records

def update_attendance_record(roll_number, attendance_date, new_status):
    if new_status not in ["Present", "Absent", "Late"]:
        return False, "Invalid attendance status!"
    try:
        parsed_date = date.fromisoformat(attendance_date)
        if parsed_date.isoformat() != attendance_date:
            return False, "Use date format YYYY-MM-DD."
    except ValueError:
        return False, "Invalid date!"
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE attendance
            SET status = ?
            WHERE student_id = (
                SELECT student_id FROM students WHERE roll_number = ?
            )
            AND date = ?
        """, (new_status, roll_number, attendance_date))
        if cursor.rowcount == 0:
            return False, "Attendance record not found!"
        conn.commit()
        return True, "Attendance updated successfully!"
    finally:
        conn.close()

def mark_attendance():
    print("\n--- Mark Attendance ---")
    roll_number = input("Enter student roll number: ").strip()

    print("1. Present")
    print("2. Absent")
    print("3. Late")

    statuses = {"1": "Present", "2": "Absent", "3": "Late"}
    choice = input("Select attendance status: ").strip()

    if choice not in statuses:
        print("Invalid choice!")
        return

    attendance_date = input(
        f"Enter date (YYYY-MM-DD) or press Enter for today [{date.today()}]: "
    ).strip()

    success, message = mark_attendance_record(
        roll_number, attendance_date, statuses[choice]
    )
    print(message)


def view_attendance():
    print("\n--- Attendance Records ---")
    records = get_all_attendance()

    if not records:
        print("No attendance records found.")
        return

    for record in records:
        print(
            f"Name: {record[1]} | Roll: {record[2]} | "
            f"Date: {record[3]} | Status: {record[4]}"
        )


def view_attendance_by_date():
    print("\n--- Date-wise Attendance Report ---")
    selected_date = input("Enter date (YYYY-MM-DD): ").strip()

    records = get_attendance_by_date(selected_date)

    if not records:
        print("No attendance records found for this date.")
        return

    for record in records:
        print(
            f"Name: {record[1]} | Roll: {record[2]} | "
            f"Date: {record[3]} | Status: {record[4]}"
        )


def view_student_attendance():
    print("\n--- Student Attendance History ---")
    roll_number = input("Enter student roll number: ").strip()

    student, records = get_student_attendance(roll_number)

    if not student:
        print("Student not found!")
        return

    print(f"\nAttendance History: {student[1]}")
    print(f"Roll Number: {roll_number}")

    if not records:
        print("No attendance history found.")
        return

    for record in records:
        print(f"Date: {record[0]} | Status: {record[1]}")


def update_attendance():
    print("\n--- Update Attendance Record ---")
    roll_number = input("Enter student roll number: ").strip()
    attendance_date = input("Enter attendance date (YYYY-MM-DD): ").strip()
    new_status = input(
        "Enter new status (Present/Absent/Late): "
    ).strip().capitalize()

    success, message = update_attendance_record(
        roll_number, attendance_date, new_status
    )
    print(message)

def update_attendance_by_id(attendance_id, new_status):
    if new_status not in ["Present", "Absent", "Late"]:
        return False, "Invalid attendance status!"
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE attendance
            SET status = ?
            WHERE attendance_id = ?
        """, (new_status, attendance_id))
        if cursor.rowcount == 0:
            return False, "Attendance record not found!"
        conn.commit()
        return True, "Attendance updated successfully!"
    finally:
        conn.close()
