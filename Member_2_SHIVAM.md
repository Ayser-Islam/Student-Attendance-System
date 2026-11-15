# MEMBER 2 – SHIVAM
## Attendance Management System – Assigned Responsibilities

### 1. Login Page and Authentication (Admin & Teacher)

- Develop the login page for Admin and Teacher.
- Implement credential-based authentication.
- Verify login credentials before granting access.
- Implement role-based authentication for Admin and Teacher.
- Only users with Admin-authorized credentials can access the system.
- Teachers cannot register or create their own accounts.

### 2. User Management (Admin Only)

- Implement user management functionality.
- Allow only the Admin to create new accounts.
- Allow the Admin to manage existing user accounts.
- Manage teacher account credentials and access.
- Restrict account creation and user-management permissions to the Admin.

### 3. Attendance Analytics

- Develop the attendance analytics section.
- Display student attendance statistics and summaries.
- Calculate and display attendance percentages.
- Provide graphical representations of attendance data.
- Help identify students with low attendance.
- Display relevant attendance trends and performance.

### 4. Attendance Defaulter List (View Defaulter List)

- Implement the Attendance Defaulter List feature.
- Identify students whose attendance is below the required threshold.
- Automatically calculate attendance percentages.
- Mark students with insufficient attendance as defaulters.
- Create a dedicated **View Defaulter List** section.
- Display student details and attendance percentages.
- Provide filtering options to view defaulter records.

### 5. Role-Based Access Control

**Admin permissions:**
- Access the Admin dashboard.
- Create and manage user accounts.
- Access attendance analytics.
- View attendance defaulter lists.
- Access attendance reports.
- Manage authorized system access.

**Teacher permissions:**
- Log in using Admin-created credentials.
- Access permitted attendance-management features.
- View attendance analytics.
- View attendance defaulter lists.
- Export attendance reports if permitted.
- Cannot create accounts or manage users.

### 6. Export Attendance Reports

- Implement attendance report export functionality.
- Generate downloadable attendance reports.
- Include student attendance details.
- Include attendance percentages.
- Include attendance summaries and defaulter information.
- Support CSV and/or PDF export formats.

### 7. Testing and Integration

- Test Admin and Teacher authentication.
- Verify that only Admin can create accounts.
- Test role-based access restrictions.
- Test attendance analytics and graphical displays.
- Verify correct defaulter identification and filtering.
- Test attendance report exports.
- Integrate all assigned modules with the main Flask application.
- Resolve bugs and integration issues.


Important commit messages:

- `Implement authentication with login and logout for admin and teacher authentication`
- `Update attendance analytics functionality`
- `Add attendance analytics dashboard`
- `Implement attendance defaulter list`
- `Add analytics and defaulter dashboard templates`
- `Implement attendance report export`
- `Implement admin account setup and user management dashboardt`




