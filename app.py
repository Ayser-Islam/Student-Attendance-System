
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    make_response
)

from datetime import date
import os
import csv
import io

from database import get_connection, initialize_database

from auth import (
    init_auth_table,
    authenticate_user,
    login_required
)

from attendance import (
    mark_attendance_record,
    get_all_attendance,
    get_attendance_by_date,
    update_attendance_by_id
)

from students import (
    add_student_record,
    get_all_students,
    search_student_record,
    update_student_record,
    delete_student_record
)

from analytics import (
    get_attendance_analytics,
    get_defaulters,
    get_student_analytics
)


# ==========================================
# FLASK APPLICATION CONFIGURATION
# ==========================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "change-this-secret-key-for-local-development"
)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Initialize database tables
initialize_database()

# Initialize authentication table
init_auth_table()


# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":

        user_id = request.form.get("user_id", "").strip()
        password = request.form.get("password", "")

        success, authenticated_id = authenticate_user(
            user_id, password
        )

        if success:
            session.clear()
            session["user_id"] = authenticated_id

            flash("Login successful!", "success")

            return redirect(url_for("home"))

        flash("Invalid login ID or password.", "error")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():

    session.clear()

    flash("You have been logged out.", "success")

    return redirect(url_for("login"))


# ==========================================
# HOME / DASHBOARD ROUTE
# ==========================================

@app.route("/")
@login_required
def home():

    return render_template("index.html")


# ==========================================
# ATTENDANCE ROUTES - MEMBER 1
# ==========================================

@app.route("/attendance", methods=["GET", "POST"])
@login_required
def attendance():

    message = None
    success = False

    if request.method == "POST":

        roll_number = request.form.get(
            "roll_number", ""
        ).strip()

        attendance_date = request.form.get(
            "attendance_date", ""
        )

        status = request.form.get("status", "")

        success, message = mark_attendance_record(
            roll_number,
            attendance_date,
            status
        )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT roll_number, name
        FROM students
        ORDER BY name
    """)

    students = cursor.fetchall()
    conn.close()

    return render_template(
        "attendance.html",
        students=students,
        today=date.today().isoformat(),
        message=message,
        success=success
    )


@app.route("/records")
@login_required
def records():

    selected_date = request.args.get(
        "date", ""
    ).strip()

    if selected_date:
        records = get_attendance_by_date(selected_date)
    else:
        records = get_all_attendance()

    return render_template(
        "records.html",
        records=records,
        selected_date=selected_date
    )


@app.route(
    "/edit-attendance/<int:attendance_id>",
    methods=["GET", "POST"]
)
@login_required
def edit_attendance(attendance_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            a.attendance_id,
            s.name,
            s.roll_number,
            a.date,
            a.status
        FROM attendance a
        JOIN students s
            ON a.student_id = s.student_id
        WHERE a.attendance_id = ?
    """, (attendance_id,))

    record = cursor.fetchone()
    conn.close()

    if not record:
        return "Attendance record not found", 404

    if request.method == "POST":

        new_status = request.form.get("status", "")

        success, message = update_attendance_by_id(
            attendance_id,
            new_status
        )

        flash(
            message,
            "success" if success else "error"
        )

        return redirect(url_for("records"))

    return render_template(
        "edit_attendance.html",
        record=record
    )


# ==========================================
# STUDENT ROUTES - MEMBER 1
# ==========================================

@app.route("/students")
@login_required
def students_page():

    search = request.args.get(
        "search", ""
    ).strip()

    if search:
        students = search_student_record(search)
    else:
        students = get_all_students()

    return render_template(
        "students.html",
        students=students,
        search=search
    )


@app.route("/students/add", methods=["POST"])
@login_required
def add_student():

    name = request.form.get("name", "")
    roll_number = request.form.get("roll_number", "")
    course = request.form.get("course", "")
    semester = request.form.get("semester", "")

    success, message = add_student_record(
        name,
        roll_number,
        course,
        semester
    )

    flash(
        message,
        "success" if success else "error"
    )

    return redirect(url_for("students_page"))


@app.route(
    "/students/edit/<roll_number>",
    methods=["GET", "POST"]
)
@login_required
def edit_student(roll_number):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, roll_number, course, semester
        FROM students
        WHERE roll_number = ?
    """, (roll_number,))

    student = cursor.fetchone()
    conn.close()

    if not student:
        return "Student not found", 404

    if request.method == "POST":

        name = request.form.get("name", "")
        course = request.form.get("course", "")
        semester = request.form.get("semester", "")

        success, message = update_student_record(
            roll_number,
            name,
            course,
            semester
        )

        flash(
            message,
            "success" if success else "error"
        )

        return redirect(url_for("students_page"))

    return render_template(
        "edit_student.html",
        student=student
    )


@app.route(
    "/students/delete/<roll_number>",
    methods=["POST"]
)
@login_required
def delete_student(roll_number):

    success, message = delete_student_record(
        roll_number
    )

    flash(
        message,
        "success" if success else "error"
    )

    return redirect(url_for("students_page"))


# ==========================================
# ATTENDANCE ANALYTICS - MEMBER 2
# ==========================================

@app.route("/analytics")
@login_required
def analytics_page():

    students = get_attendance_analytics()

    total_students = len(students)

    total_present = sum(
        student["present"] for student in students
    )

    total_absent = sum(
        student["absent"] for student in students
    )

    total_late = sum(
        student["late"] for student in students
    )

    total_classes = sum(
        student["total"] for student in students
    )

    overall_percentage = (
        ((total_present + total_late) / total_classes) * 100
        if total_classes > 0 else 0
    )

    return render_template(
        "analytics.html",
        students=students,
        total_students=total_students,
        total_present=total_present,
        total_absent=total_absent,
        total_late=total_late,
        overall_percentage=round(
            overall_percentage, 2
        )
    )


# ==========================================
# STUDENT-WISE ATTENDANCE SUMMARY - MEMBER 2
# ==========================================

@app.route("/analytics/student/<roll_number>")
@login_required
def student_analytics(roll_number):

    student = get_student_analytics(roll_number)

    if not student:
        return "Student not found", 404

    return render_template(
        "student_analytics.html",
        student=student
    )


# ==========================================
# DEFAULTER IDENTIFICATION - MEMBER 2
# ==========================================

@app.route("/defaulters")
@login_required
def defaulters_page():

    threshold = request.args.get(
        "threshold", "75"
    )

    try:
        threshold = float(threshold)

        if not 0 <= threshold <= 100:
            raise ValueError

    except ValueError:

        flash(
            "Enter a valid threshold between 0 and 100.",
            "error"
        )

        return redirect(url_for("defaulters_page"))

    defaulters = get_defaulters(threshold)

    return render_template(
        "defaulters.html",
        defaulters=defaulters,
        threshold=threshold
    )


# ==========================================
# ATTENDANCE REPORT - CSV EXPORT - MEMBER 2
# ==========================================

@app.route("/reports/export")
@login_required
def export_attendance():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            s.name,
            s.roll_number,
            s.course,
            s.semester,
            a.date,
            a.status
        FROM attendance a
        JOIN students s
            ON a.student_id = s.student_id
        ORDER BY a.date DESC, s.name
    """)

    records = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Student Name",
        "Roll Number",
        "Course",
        "Semester",
        "Date",
        "Attendance Status"
    ])

    writer.writerows(records)

    response = make_response(output.getvalue())

    response.headers["Content-Disposition"] = (
        "attachment; filename=attendance_report.csv"
    )

    response.headers["Content-Type"] = (
        "text/csv; charset=utf-8"
    )

    return response


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)
