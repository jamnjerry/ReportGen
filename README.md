# ReportGen - A KivyMD Application

## Overview
ReportGen is a desktop application built using Kivy and KivyMD that allows teachers to manage courses, students, and grades. It provides a user-friendly interface to view course details, track student performance, and update grades dynamically using a MySQL database.

---

## Features
- **Dynamic Table Management:**
  - View a list of courses and their corresponding class IDs.
  - Access student information and grades for a selected course.
- **Grade Updates:**
  - Update student grades for individual terms (T1, T2, T3) using dialog forms.
- **MySQL Integration:**
  - Real-time data fetching and updating using a MySQL database.
- **Screen Navigation:**
  - Seamless navigation between screens: Main Screen, Course Screen, and Grades Dialog.
- **User-Friendly Interface:**
  - Built with KivyMD components for a clean and modern design.

---

## Technologies Used
1. **Python Libraries:**
   - [Kivy](https://kivy.org/): For creating the GUI.
   - [KivyMD](https://kivymd.readthedocs.io/): For Material Design components.
   - [MySQL Connector](https://dev.mysql.com/doc/connector-python/en/): For interacting with the MySQL database.
2. **Database:**
   - MySQL: To store and manage data for courses, students, and grades.

---

## Prerequisites
To run this project, ensure the following are installed:

1. **Python 3.7+**
2. **Required Python Packages:**
   ```bash
   pip install kivy kivymd mysql-connector-python
   ```
3. **MySQL Database:**
   - Create a MySQL database named `gradingrpa`.
   - Ensure you have tables such as `course`, `student`, and `grade` with the correct schema.

---

## Project Structure
```
.
├── main.py           # Main Python application file
├── reportgen.kv      # Kivy language file defining the UI
├── README.md         # Documentation file (this file)
```

---

## How to Run the Application

1. **Set Up the Database:**
   - Create the `gradingrpa` database and tables (e.g., `course`, `student`, and `grade`).
   - Insert some test data to interact with.

2. **Run the Application:**
   - Execute the following command:
     ```bash
     python main.py
     ```

3. **Navigate the App:**
   - Start at the Main Screen to view courses.
   - Click on a course row to view and manage student grades.
   - Use the input fields to update term grades.

---

## Database Schema
Ensure the following tables are available in your database:

### `course`
| ID   | Course Name     | Class ID |
|------|-----------------|----------|
| INT  | VARCHAR(255)    | INT      |

### `student`
| ID   | First Name | Last Name | Class |
|------|------------|-----------|-------|
| INT  | VARCHAR(255) | VARCHAR(255) | INT |

### `grade`
| ID   | Student ID | Course ID | Term 1 | Term 2 | Term 3 |
|------|------------|-----------|--------|--------|--------|
| INT  | INT        | INT       | FLOAT  | FLOAT  | FLOAT  |

---

## Future Enhancements
1. Add user authentication for teachers.
2. Implement reporting tools to generate PDF reports of grades.
3. Allow bulk uploads of student grades using CSV files.

---

## License
This project is licensed under the MIT License. Feel free to use and modify it as needed.

---

## Credits
Developed by Devine Kalekyezi.

For questions or feedback, feel free to reach out!

