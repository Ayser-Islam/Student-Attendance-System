
from database import get_connection


def get_attendance_analytics():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            s.student_id,
            s.name,
            s.roll_number,
            s.course,
            s.semester,
            COUNT(a.attendance_id),
            SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END),
            SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END),
            SUM(CASE WHEN a.status = 'Late' THEN 1 ELSE 0 END)
        FROM students s
        LEFT JOIN attendance a
            ON s.student_id = a.student_id
        GROUP BY s.student_id
        ORDER BY s.name
    """)

    records = cursor.fetchall()
    conn.close()

    students = []

    for record in records:
        total = record[5] or 0
        present = record[6] or 0
        absent = record[7] or 0
        late = record[8] or 0

        attended = present + late

        percentage = (
            (attended / total) * 100
            if total > 0 else 0
        )

        students.append({
            "student_id": record[0],
            "name": record[1],
            "roll_number": record[2],
            "course": record[3],
            "semester": record[4],
            "total": total,
            "present": present,
            "absent": absent,
            "late": late,
            "percentage": round(percentage, 2)
        })

    return students


def get_defaulters(threshold=75):
    students = get_attendance_analytics()

    return [
        student for student in students
        if student["percentage"] < threshold
    ]


def get_student_analytics(roll_number):
    students = get_attendance_analytics()

    for student in students:
        if student["roll_number"] == roll_number:
            return student

    return None
