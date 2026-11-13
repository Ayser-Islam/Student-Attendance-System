from database import get_connection
from datetime import date

def mark_attendance():
    print("\n--- Mark Attendance ---")
    roll_number = input("Enter student roll number: ").strip()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT student_id, name FROM students WHERE roll_number = ?",
        (roll_number,)
    )
    student = cursor.fetchone()
    if not student:
        print("Student not found!")
        conn.close()
        return
    student_id, name = student
    print(f"\nStudent: {name}")
    print("1. Present")
    print("2. Absent")
    print("3. Late")
    choice = input("Select attendance status: ")
    statuses = {
        "1": "Present",
        "2": "Absent",
        "3": "Late"
    }
    if choice not in statuses:
        print("Invalid choice!")
        conn.close()
        return
    attendance_status = statuses[choice]
    attendance_date = input(
        f"Enter date (YYYY-MM-DD) or press Enter for today [{date.today()}]: "
    ).strip()
    if not attendance_date:
        attendance_date = date.today().isoformat()
    try:
        date.fromisoformat(attendance_date)
        cursor.execute("""
            INSERT INTO attendance (student_id, date, status)
            VALUES (?, ?, ?)
        """, (student_id, attendance_date, attendance_status))
        conn.commit()
        print(f"\nAttendance marked: {attendance_status}")
    except ValueError:
        print("Invalid date format!")
    except Exception:
        print("Attendance already marked for this student on this date.")
    finally:
        conn.close()

def view_attendance():
    print("\n--- Attendance Records ---")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.name, s.roll_number, a.date, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        ORDER BY a.date DESC
    """)
    records = cursor.fetchall()
    if not records:
        print("No attendance records found.")
    else:
        for record in records:
            print(
                f"Name: {record[0]} | "
                f"Roll: {record[1]} | "
                f"Date: {record[2]} | "
                f"Status: {record[3]}"
            )
    conn.close()

def view_attendance_by_date():
    print("\n--- Date-wise Attendance Report ---")
    selected_date = input("Enter date (YYYY-MM-DD): ").strip()
    try:
        date.fromisoformat(selected_date)
    except ValueError:
        print("Invalid date! Use YYYY-MM-DD format.")
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.name, s.roll_number, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        WHERE a.date = ?
        ORDER BY s.name
    """, (selected_date,))
    records = cursor.fetchall()
    conn.close()
    if not records:
        print("No attendance records found for this date.")
        return
    print(f"\nAttendance Report for {selected_date}")
    print("-" * 50)
    for record in records:
        print(
            f"Name: {record[0]} | "
            f"Roll: {record[1]} | "
            f"Status: {record[2]}"
        )
    print("-" * 50)
    print(f"Total records: {len(records)}")

def view_student_attendance():
    print("\n--- Student Attendance History ---")
    roll_number = input("Enter student roll number: ").strip()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT student_id, name
        FROM students
        WHERE roll_number = ?
    """, (roll_number,))
    student = cursor.fetchone()
    if not student:
        print("Student not found!")
        conn.close()
        return
    cursor.execute("""
        SELECT date, status
        FROM attendance
        WHERE student_id = ?
        ORDER BY date DESC
    """, (student[0],))
    records = cursor.fetchall()
    conn.close()
    print(f"\nAttendance History: {student[1]}")
    print(f"Roll Number: {roll_number}")
    print("-" * 40)
    if not records:
        print("No attendance history found.")
        return
    for record in records:
        print(f"Date: {record[0]} | Status: {record[1]}")
    print("-" * 40)
    print(f"Total attendance records: {len(records)}")
    
def update_attendance():
    print("\n--- Update Attendance Record ---")
    roll_number = input("Enter student roll number: ").strip()
    date = input("Enter attendance date (YYYY-MM-DD): ").strip()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.student_id, s.name, a.status
        FROM students s
        JOIN attendance a ON s.student_id = a.student_id
        WHERE s.roll_number = ? AND a.date = ?
    """, (roll_number, date))
    record = cursor.fetchone()
    if not record:
        print("Attendance record not found!")
        conn.close()
        return
    print(f"Student: {record[1]}")
    print(f"Current status: {record[2]}")
    new_status = input(
        "Enter new status (Present/Absent/Late): "
    ).strip().capitalize()
    if new_status not in ["Present", "Absent", "Late"]:
        print("Invalid status!")
        conn.close()
        return
    cursor.execute("""
        UPDATE attendance
        SET status = ?
        WHERE student_id = ? AND date = ?
    """, (new_status, record[0], date))
    conn.commit()
    conn.close()
    print("Attendance record updated successfully!")