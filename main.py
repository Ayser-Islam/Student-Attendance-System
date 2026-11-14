from attendance import (
    mark_attendance,
    view_attendance,
    view_attendance_by_date,
    view_student_attendance,
    update_attendance
)
from database import initialize_database
from students import (
    add_student,
    view_students,
    search_student,
    delete_student,
    update_student
)

def main():
    initialize_database()

    while True:
       print("\n================================")
       print("  STUDENT ATTENDANCE SYSTEM")
       print("================================")
       print("1. Add Student")
       print("2. View All Students")
       print("3. Search Student")
       print("4. Delete Student")
       print("5. Update Student")
       print("6. Mark Attendance")
       print("7. View Attendance Records")
       print("8. View Attendance by Date")
       print("9. View Student Attendance History")
       print("10. Update Attendance Record")
       print("11. Exit")

       choice = input("\nEnter your choice: ")
       if choice == "1":
           add_student()
       elif choice == "2":
           view_students()
       elif choice == "3":
           search_student()
       elif choice == "4":
           delete_student()
       elif choice == "5":
           update_student()
       elif choice == "6":
           mark_attendance()
       elif choice == "7":
           view_attendance()
       elif choice == "8":
           view_attendance_by_date()
       elif choice == "9":
           view_student_attendance()
       elif choice == "10":
           update_attendance()
       elif choice == "11":
           print("Thank you for using the system!")
           break

if __name__ == "__main__":
    main()
