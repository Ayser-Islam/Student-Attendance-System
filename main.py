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
        print("6. Exit")

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
            print("Thank you for using the system!")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
