
# stuAtt:  Student Attendance Management System

## 1. Project Description

**stuAtt** is a web-based Student Attendance Management System developed as part of the SEC assignment by Ayser Islam and Shivam Chaudhary.

It provides a centralized platform for managing student records, recording attendance, monitoring attendance performance, identifying defaulters and generating attendance reports.


## 2. Project Objectives

- Maintain student information in a centralized database.
- Simplify attendance marking, updating, searching and filtering.
- Provide login and role-based access for application users.
- Monitor student attendance percentages.
- Identify students with low attendance.
- Generate downloadable attendance reports.
- Practise collaborative development using Git and GitHub.

## 3. Team Members and Contributions

| Member | Course | Roll Number | Contributions |
|---|---|---|---|
| Ayser Islam | MCA | 17 | Student and attendance databases and their CRUD operations, main teacher web interface and dashboard, attendance marking and updation, student search and updation, attendance filtering, shared navigation and consistent page layouts and a warning system  |
| Shivam Chaudhary | MCA | 55 | Teacher login and authentication, admin login, admin dashboard and commands, user account management, attendance analytics and statistics, attendance percentage calculation, defaulter identification and filtering, CSV attendance report generation |

Both members collaborated on application integration, testing, Git branching, pull requests, code reviews and merge-conflict resolution.

## 4. Project Features

### 4.1 Student Management and Records

- Register students with name, roll number, course and semester.
- Search students by name or roll number.
- Edit and delete student information.
- Prevent deletion of students with linked attendance records.

### 4.2 Attendance Management

- Mark attendance as Present, Absent or Late.
- Prevent duplicate attendance entries.
- View attendance records.
- Filter records by date.
- Edit existing attendance entries.

### 4.3 Web Interface and Navigation

- Flask-based web application.
- Teacher dashboard.
- Shared navigation and consistent page layouts.
- Student and attendance management pages.

### 4.4 Authentication and Account Management

- Login and logout functionality.
- Role-based access for administrators and teachers.
- Admin dashboard and account management.
- Create and manage user accounts.
- Password reset functionality.

### 4.5 Attendance Analytics and Defaulter Monitoring

- Display attendance statistics.
- Calculate attendance percentages.
- View student-wise attendance summaries.
- Identify students below the attendance threshold.
- View and filter the defaulter list.

### 4.6 Attendance Report Generation

- Export attendance records to CSV.
- Download attendance data for reporting and record-keeping.

## 5. Technologies Used

- **Python** – Core programming language.
- **Flask** – Web application framework.
- **SQLite** – Database management.
- **HTML5** – Webpage structure.
- **CSS3** – Styling and layout.
- **Jinja2** – Template rendering.
- **Git** – Version control.
- **GitHub** – Repository hosting and collaboration.

## 6. Project Structure

```text
Student-Attendance-System/
│
├── app.py
├── attendance.py
├── students.py
├── database.py
├── analytics.py
├── auth.py
├── reset_password.py
├── setup_users.py
├── check_users.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   └── Other HTML templates
│
├── static/
│   └── css/
│       └── style.css
│
├── .gitignore
├── README.md
└── CONTRIBUTING.md
```

The `templates/` directory contains the HTML and Jinja2 pages used by the application. The `static/` directory contains CSS styling and other static assets. Python modules contain the application routes and student, attendance, database, authentication and analytics logic.


## 7. Installation and Execution

### Prerequisites
- Python installed on your computer.
- Git installed on your computer.

### Step 1: Clone the Repository

```bash
git clone https://github.com/Ayser-Islam/Student-Attendance-System.git
cd Student-Attendance-System
```

### Step 2: Create a Virtual Environment

```powershell
py -m venv .venv
```

### Step 3: Activate the Virtual Environment

```powershell
.venv\Scripts\Activate.ps1
```

### Step 4: Install Flask

```powershell
py -m pip install flask
```

### Step 5: Configure the Secret Key

The application requires the `SECRET_KEY` environment variable.

Set your own long, random secret key:

```powershell
$env:SECRET_KEY = "your-own-long-random-secret-key"
```

Do not publish or commit your actual secret key.

### Step 6: Initial Admin Account Setup

Before accessing the application for the first time, create an administrator account.

Run the setup script:

```powershell
py setup_users.py
```

The script will prompt you for:

- Admin Login ID
- Admin Password
- Confirm Admin Password

**Password requirements:**
- Minimum 8 characters.
- Both password entries must match.

The password is entered securely and is not displayed in the terminal.

After successful creation, you will see:

```text
Admin account setup completed!
You can now log in to the Flask application.
```

If an admin account already exists, the script displays its Login ID instead of creating another account.

### Step 7: Run the Application

```powershell
py app.py
```

Open the local URL displayed in the terminal in your browser.

### Step 8: Login to the Application

1. Navigate to the login page.
2. Select the appropriate user role.
3. Enter your Login ID and Password.
4. Click Login.

After successful admin login, access the Admin Dashboard to:

- Create teacher and student accounts.
- Manage existing user accounts.
- Perform administrative operations.

**Important:** Keep your admin credentials private. The `SECRET_KEY` environment variable applies only to the current PowerShell session. Set it again when opening a new terminal.



## 9. Screenshots
<img width="624" height="287" alt="Picture1" src="https://github.com/user-attachments/assets/5e44bb15-d1bd-4c70-b585-bf3e6ae39f8e" />
<img width="626" height="198" alt="Picture2" src="https://github.com/user-attachments/assets/f904b467-5b0d-48f8-b213-1b7968d5faff" />
<img width="829" height="506" alt="Picture3" src="https://github.com/user-attachments/assets/f92b6d03-f3ed-422c-a6a2-bd6552da3df5" />
<img width="780" height="385" alt="Picture4" src="https://github.com/user-attachments/assets/d4da4025-22e3-4834-8989-c3175ebf78d4" />



