
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    make_response,
    abort
)

from datetime import date
import os
import csv
import io

from database import get_connection, initialize_database

from auth import (
    init_auth_table,
    create_auth_user,
    authenticate_user,
    login_required,
    role_required
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

initialize_database()
init_auth_table()


# ==========================================
# CHECK ACTIVE USER SESSION
# ==========================================

@app.before_request
def check_active_session():

    user_id = session.get("user_id")

    if not user_id:
        return None

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, role, student_id, is_active
        FROM auth_users
        WHERE user_id = ?
    """, (user_id,))

    user = cursor.fetchone()
    conn.close()

    if not user or not user[3]:

        session.clear()

        if request.endpoint != "login":
            flash(
                "Your account is inactive or no longer exists. Please log in again.",
                "error"
            )

            return redirect(url_for("login"))

        return None

    session["user_id"] = user[0]
    session["role"] = user[1]
    session["student_id"] = user[2]

    return None


# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":

        user_id = request.form.get(
            "user_id", ""
        ).strip()

        password = request.form.get(
            "password", ""
        )

        success, user = authenticate_user(
            user_id,
            password
        )

        if success:

            session.clear()

            session["user_id"] = user["user_id"]
            session["role"] = user["role"]
            session["student_id"] = user["student_id"]

            flash(
                "Login successful!",
                "success"
            )

            return redirect(url_for("home"))

        flash(
            "Invalid login ID or password.",
            "error"
        )

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("login"))


# ==========================================
# HOME / ROLE-BASED DASHBOARD
# ==========================================

@app.route("/")
@login_required
def home():

    role = session.get("role")

    if role == "admin":
        return redirect(url_for("admin_dashboard"))

    if role == "student":
        return redirect(url_for("my_attendance"))

    if role == "teacher":
        return render_template("index.html")

    abort(403)


# ==========================================
# ADMIN DASHBOARD
# ==========================================

@app.route("/admin")
@role_required("admin")
def admin_dashboard():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            u.user_id,
            u.role,
            u.created_at,
            u.is_active,
            s.name,
            s.roll_number
        FROM auth_users u
        LEFT JOIN students s
            ON u.student_id = s.student_id
        ORDER BY u.created_at DESC
    """)

    users = cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(*)
        FROM auth_users
        WHERE role = 'teacher'
    """)

    total_teachers = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM auth_users
        WHERE role = 'student'
    """)

    total_student_accounts = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin_dashboard.html",
        users=users,
        total_teachers=total_teachers,
        total_student_accounts=total_student_accounts
    )


# ==========================================
# CREATE TEACHER / STUDENT ACCOUNT
# ==========================================

@app.route(
    "/admin/create-user",
    methods=["GET", "POST"]
)
@role_required("admin")
def create_user():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT student_id, name, roll_number
        FROM students
        ORDER BY name
    """)

    students = cursor.fetchall()
    conn.close()

    if request.method == "POST":

        user_id = request.form.get(
            "user_id", ""
        ).strip()

        password = request.form.get(
            "password", ""
        )

        role = request.form.get(
            "role", ""
        ).strip()

        student_id = None

        if role == "student":

            roll_number = request.form.get(
                "roll_number", ""
            ).strip()

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT student_id
                FROM students
                WHERE roll_number = ?
            """, (roll_number,))

            student = cursor.fetchone()
            conn.close()

            if not student:

                flash(
                    "Please select a valid student.",
                    "error"
                )

                return render_template(
                    "create_staff.html",
                    students=students
                )

            student_id = student[0]

        if role not in ("teacher", "student"):

            flash(
                "Invalid account role.",
                "error"
            )

            return render_template(
                "create_staff.html",
                students=students
            )

        success, message = create_auth_user(
            user_id,
            password,
            role,
            student_id
        )

        flash(
            message,
            "success" if success else "error"
        )

        if success:
            return redirect(
                url_for("admin_dashboard")
            )

    return render_template(
        "create_staff.html",
        students=students
    )


# ==========================================
# ACTIVATE / DEACTIVATE USER ACCOUNT
# ==========================================

@app.route(
    "/admin/toggle-user/<user_id>",
    methods=["POST"]
)
@role_required("admin")
def toggle_user(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, is_active
        FROM auth_users
        WHERE user_id = ?
    """, (user_id,))

    user = cursor.fetchone()

    if not user:

        conn.close()

        flash(
            "User not found.",
            "error"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    if user[0] == "admin":

        conn.close()

        flash(
            "Admin accounts cannot be disabled here.",
            "error"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    new_status = 0 if user[1] else 1

    cursor.execute("""
        UPDATE auth_users
        SET is_active = ?
        WHERE user_id = ?
    """, (new_status, user_id))

    conn.commit()
    conn.close()

    flash(
        "Account status updated successfully.",
        "success"
    )

    return redirect(
        url_for("admin_dashboard")
    )


# ==========================================
# ATTENDANCE ROUTES - ADMIN / TEACHER
# ==========================================

@app.route(
    "/attendance",
    methods=["GET", "POST"]
)
@role_required("admin", "teacher")
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

        status = request.form.get(
            "status", ""
        )

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
@role_required("admin", "teacher")
def records():

    selected_date = request.args.get(
        "date", ""
    ).strip()

    if selected_date:
        attendance_records = get_attendance_by_date(
            selected_date
        )
    else:
        attendance_records = get_all_attendance()

    return render_template(
        "records.html",
        records=attendance_records,
        selected_date=selected_date
    )


@app.route(
    "/edit-attendance/<int:attendance_id>",
    methods=["GET", "POST"]
)
@role_required("admin", "teacher")
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

        new_status = request.form.get(
            "status", ""
        )

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
# STUDENT MANAGEMENT - ADMIN / TEACHER
# ==========================================

@app.route("/students")
@role_required("admin", "teacher")
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


@app.route(
    "/students/add",
    methods=["POST"]
)
@role_required("admin", "teacher")
def add_student():

    name = request.form.get(
        "name", ""
    )

    roll_number = request.form.get(
        "roll_number", ""
    )

    course = request.form.get(
        "course", ""
    )

    semester = request.form.get(
        "semester", ""
    )

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

    return redirect(
        url_for("students_page")
    )


@app.route(
    "/students/edit/<roll_number>",
    methods=["GET", "POST"]
)
@role_required("admin", "teacher")
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

        name = request.form.get(
            "name", ""
        )

        course = request.form.get(
            "course", ""
        )

        semester = request.form.get(
            "semester", ""
        )

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

        return redirect(
            url_for("students_page")
        )

    return render_template(
        "edit_student.html",
        student=student
    )


@app.route(
    "/students/delete/<roll_number>",
    methods=["POST"]
)
@role_required("admin", "teacher")
def delete_student(roll_number):

    success, message = delete_student_record(
        roll_number
    )

    flash(
        message,
        "success" if success else "error"
    )

    return redirect(
        url_for("students_page")
    )


# ==========================================
# ATTENDANCE ANALYTICS - ADMIN / TEACHER
# ==========================================

@app.route("/analytics")
@role_required("admin", "teacher")
def analytics_page():

    students = get_attendance_analytics()

    total_students = len(students)

    total_present = sum(
        student["present"]
        for student in students
    )

    total_absent = sum(
        student["absent"]
        for student in students
    )

    total_late = sum(
        student["late"]
        for student in students
    )

    total_classes = sum(
        student["total"]
        for student in students
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


@app.route(
    "/analytics/student/<roll_number>"
)
@role_required("admin", "teacher")
def student_analytics(roll_number):

    student = get_student_analytics(
        roll_number
    )

    if not student:
        return "Student not found", 404

    return render_template(
        "student_analytics.html",
        student=student
    )


# ==========================================
# DEFAULTER IDENTIFICATION
# ==========================================

@app.route("/defaulters")
@role_required("admin", "teacher")
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

        return redirect(
            url_for("defaulters_page")
        )

    defaulters = get_defaulters(
        threshold
    )

    return render_template(
        "defaulters.html",
        defaulters=defaulters,
        threshold=threshold
    )


# ==========================================
# STUDENT PERSONAL ATTENDANCE DASHBOARD
# ==========================================

@app.route("/my-attendance")
@role_required("student")
def my_attendance():

    student_id = session.get(
        "student_id"
    )

    if not student_id:
        abort(403)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            student_id,
            name,
            roll_number,
            course,
            semester
        FROM students
        WHERE student_id = ?
    """, (student_id,))

    student = cursor.fetchone()

    if not student:

        conn.close()

        return "Student record not found", 404

    cursor.execute("""
        SELECT date, status
        FROM attendance
        WHERE student_id = ?
        ORDER BY date DESC
    """, (student_id,))

    attendance_records = cursor.fetchall()

    cursor.execute("""
        SELECT
            COUNT(*),
            SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END),
            SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END),
            SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END)
        FROM attendance
        WHERE student_id = ?
    """, (student_id,))

    statistics = cursor.fetchone()

    conn.close()

    total = statistics[0] or 0
    present = statistics[1] or 0
    absent = statistics[2] or 0
    late = statistics[3] or 0

    percentage = (
        ((present + late) / total) * 100
        if total > 0 else 0
    )

    return render_template(
        "student_dashboard.html",
        student=student,
        attendance_records=attendance_records,
        total=total,
        present=present,
        absent=absent,
        late=late,
        percentage=round(percentage, 2)
    )


# ==========================================
# ATTENDANCE REPORT - CSV EXPORT
# ==========================================

@app.route("/reports/export")
@role_required("admin", "teacher")
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
# ERROR HANDLING
# ==========================================

@app.errorhandler(403)
def forbidden(error):

    return (
        "Access denied: You do not have permission to access this page.",
        403
    )


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)
