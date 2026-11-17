from datetime import datetime
from database import get_connection


def init_leaves_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
                CHECK(status IN ('Pending', 'Approved', 'Rejected')),
            applied_on TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)

    conn.commit()
    conn.close()


def apply_leave(student_id, start_date, end_date, reason):
    if not start_date or not end_date or not reason.strip():
        return False, "All fields are required."

    if start_date > end_date:
        return False, "End date cannot be earlier than start date."

    conn = get_connection()
    cursor = conn.cursor()

    applied_on = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("""
        INSERT INTO leave_requests (student_id, start_date, end_date, reason, applied_on)
        VALUES (?, ?, ?, ?, ?)
    """, (student_id, start_date, end_date, reason.strip(), applied_on))

    conn.commit()
    conn.close()
    return True, "Leave request submitted successfully!"


def get_student_leaves(student_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT leave_id, start_date, end_date, reason, status, applied_on
        FROM leave_requests
        WHERE student_id = ?
        ORDER BY leave_id DESC
    """, (student_id,))

    leaves = cursor.fetchall()
    conn.close()
    return leaves


def get_all_leaves():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            l.leave_id,
            s.name,
            s.roll_number,
            s.course,
            l.start_date,
            l.end_date,
            l.reason,
            l.status,
            l.applied_on
        FROM leave_requests l
        JOIN students s ON l.student_id = s.student_id
        ORDER BY l.leave_id DESC
    """)

    leaves = cursor.fetchall()
    conn.close()
    return leaves


def update_leave_status(leave_id, new_status):
    if new_status not in ("Approved", "Rejected"):
        return False, "Invalid status."

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE leave_requests
        SET status = ?
        WHERE leave_id = ?
    """, (new_status, leave_id))

    if cursor.rowcount == 0:
        conn.close()
        return False, "Leave request not found."

    conn.commit()
    conn.close()
    return True, f"Leave request {new_status.lower()} successfully!"
