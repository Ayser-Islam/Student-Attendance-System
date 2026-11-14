from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date
from database import get_connection

import os
from flask import session
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
app = Flask(__name__)
app.secret_key = "attendance-project-secret-key"

@app.route("/")
def home():
    return render_template("index.html")

# ==========================================
# ATTENDANCE ROUTES
# ==========================================

@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    message = None
    success = False
    if request.method == "POST":
        roll_number = request.form.get("roll_number", "").strip()
        attendance_date = request.form.get("attendance_date", "")
        status = request.form.get("status", "")
        success, message = mark_attendance_record(
            roll_number, attendance_date, status
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
def records():
    selected_date = request.args.get("date", "").strip()
    if selected_date:
        records = get_attendance_by_date(selected_date)
    else:
        records = get_all_attendance()
    return render_template(
        "records.html",
        records=records,
        selected_date=selected_date
    )

@app.route("/edit-attendance/<int:attendance_id>", methods=["GET", "POST"])
def edit_attendance(attendance_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.attendance_id, s.name, s.roll_number, a.date, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        WHERE a.attendance_id = ?
    """, (attendance_id,))
    record = cursor.fetchone()
    conn.close()
    if not record:
        return "Attendance record not found", 404
    if request.method == "POST":
        new_status = request.form.get("status", "")
        success, message = update_attendance_by_id(
            attendance_id, new_status
        )
        flash(message, "success" if success else "error")
        return redirect(url_for("records"))
    return render_template("edit_attendance.html", record=record)

# ==========================================
# STUDENT ROUTES
# ==========================================

@app.route("/students")
def students_page():
    search = request.args.get("search", "").strip()
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
def add_student():
    name = request.form.get("name", "")
    roll_number = request.form.get("roll_number", "")
    course = request.form.get("course", "")
    semester = request.form.get("semester", "")
    success, message = add_student_record(
        name, roll_number, course, semester
    )
    flash(message, "success" if success else "error")
    return redirect(url_for("students_page"))

@app.route("/students/edit/<roll_number>", methods=["GET", "POST"])
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
            roll_number, name, course, semester
        )
        flash(message, "success" if success else "error")
        return redirect(url_for("students_page"))
    return render_template("edit_student.html", student=student)

@app.route("/students/delete/<roll_number>", methods=["POST"])
def delete_student(roll_number):
    success, message = delete_student_record(roll_number)
    flash(message, "success" if success else "error")
    return redirect(url_for("students_page"))



# ==========================================
# Add login and logout routes
# ==========================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "change-this-secret-key-for-local-development"
)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

init_auth_table()


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

@app.route("/")
@login_required
def home():
    return render_template("index.html")

@app.route("/attendance", methods=["GET", "POST"])
@login_required
def attendance():

@app.route("/edit-attendance/<int:attendance_id>", methods=["GET", "POST"])
@login_required
def edit_attendance(attendance_id):



@app.route("/students")
@login_required
def students_page():

@app.route("/students/add", methods=["POST"])
@login_required
def add_student():

@app.route("/students/edit/<roll_number>", methods=["GET", "POST"])
@login_required
def edit_student(roll_number):

@app.route("/students/delete/<roll_number>", methods=["POST"])
@login_required
def delete_student(roll_number):


if __name__ == "__main__":
    app.run(debug=True)
