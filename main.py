from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
import mysql.connector as connector
import configparser
from docx import Document

conn = connector.connect(
    host="127.0.0.1",         # Replace with your MySQL server's hostname or IP address
    user="root",              # Replace with your MySQL username
    password="Highpeople11",      # Replace with your MySQL password
    database="gradingrpa",  # Database name
    auth_plugin='mysql_native_password'
)

cursor = conn.cursor()
config = configparser.ConfigParser()
config.read('config.ini')
key = config.get('ENCRYPTION', 'key')

class Report(Screen):
    pass
class SignIn(Screen):
    pass
class MainScreen(Screen):
    pass

class CourseScreen(Screen):
    pass

class Grades(Screen):
    pass

class ReportGen(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.sm = Builder.load_file('reportgen.kv')
        return self.sm
    
    def sign_in(self, id, password):
        
        if id and password:
            cursor.execute(f"SELECT * FROM teacher WHERE id={id} AND AES_DECRYPT(password, '{key}') = '{password}' ")
            credentials = cursor.fetchall()
            if credentials:
                self.teacher = credentials[0][0]
                self.teachername = credentials[0][1] + ' ' + credentials[0][2]
                self.email = credentials[0][3]
                self.number = credentials[0][4]
                self.get_main_screen('courses')
                self.sm.get_screen('main').ids.header.title = 'Welcome ' + self.teachername
                self.sm.get_screen('main').ids.header.title_color = (1,1,1,1)
            else:
                pass
        else:
            pass
    def get_main_screen(self, screen):
        self.sm.get_screen('main').ids.box_table.clear_widgets()
        if screen == 'courses':
            self.data_table = self.create_data_table([
            ("ID", dp(30)),
            ("Course Name", dp(70)),
            ('Class ID', dp(30)),
            ], [(item[0], item[1], item[-1]) for item in self.get_all_items('course', 'teacher', self.teacher)])
            self.data_table.bind(on_row_press=self.course_row_press)
            self.sm.get_screen('main').ids.box_table.add_widget(self.data_table)
            self.sm.current = 'main'
        elif screen == 'classes':
            self.data_table = self.create_data_table([
                ("Class ID", dp(70)),
                (' ', dp(70))
            ], [(item[0], '') for item in self.get_all_items('class', 'teacher', self.teacher)])
            self.data_table.bind(on_row_press=self.class_row_press)
            self.sm.get_screen('main').ids.box_table.add_widget(self.data_table)
            pass
        self.sm.get_screen('main').ids.nav_drawer.set_state('closed')

    def create_data_table(self, column_data, row_data):
        """Create an MDDataTable widget."""
        table = MDDataTable(
            size_hint=(1, 1),
            pos_hint= {'center_x': 0.5,'center_y': 0.5},
            check=True,
            use_pagination=True,
            elevation=2,
            background_color_header="yellow",
            rows_num=5,
            column_data=column_data,
            row_data= row_data,
            
        )
        table.ids.container.radius = [0, 0, 0, 0]
        table.row_focus = [0, 0, 0, 0]
        return table

    def get_all_items(self, table, cond, val):
        cursor.execute(f"SELECT * FROM {table} WHERE {cond}={val}")
        return cursor.fetchall()
    def get_all_items_cond(self, table, cond1, val1, cond2, val2):
        cursor.execute(f"SELECT * FROM {table} WHERE {cond1}= '{val1}' AND {cond2}='{val2}'")
        return cursor.fetchall()

    def switch_to_add_item_screen(self):
        """Switch to the Add Item screen."""
        self.sm.current = 'add_item'

    def switch_to_main_screen(self):
        """Switch to the Main screen."""
        self.sm.current = 'main'

    def add_item(self, name, quantity, supplier):
        """Add an item to the inventory."""
        if not name or not quantity:
            self.show_dialog("Error", "Both fields are required.")
            return
        else:
            cursor.execute("INSERT INTO items (name, quantity, supplierid) VALUES (%s, %s, %s)", (name, quantity, supplier))
            conn.commit()
            self.update_data_table()
            self.switch_to_main_screen()

    def update_data_table(self):
        """Update the MDDataTable with the latest inventory data."""
        self.inventory = self.get_all_items()
        self.data_table.row_data = [(i + 1, item[1], item[2]) for i, item in enumerate(self.inventory)]
    
    def update_grade(self, keys, studentid, courseid):
        grade = [self.dialog.content_cls.ids.term1.text.strip(),
                self.dialog.content_cls.ids.term2.text.strip(),
                self.dialog.content_cls.ids.term3.text.strip(),
    ]   
        gradezip = zip(keys,grade)
        for key, val in gradezip:
            if val:
                print(key, val)
                cursor.execute(f'UPDATE grade SET {key}={val} WHERE studentid={studentid} AND courseid={courseid}')
                conn.commit()
                
            else:
                pass
        col_input = [('ID', dp(30)), ('Name', dp(50)), ('T1', dp(20)), ('T2', dp(20)), ('T3', dp(20))]
        cursor.execute(f'SELECT s.id, fname, lname, term1, term2, term3 from gradingrpa.student as s join gradingrpa.course as c on s.class = c.class join gradingrpa.grade as g on c.id = g.courseid WHERE g.courseid = {self.courseid} and s.class = {self.clas}')
        grade = cursor.fetchall()
        row_input = [(item[0], item[1] + ' ' + item[2], item[3], item[4], item[5]) for item in grade]
        table = self.create_data_table(col_input,row_input)
        self.sm.get_screen('course').ids.box_table.clear_widgets()
        self.sm.get_screen('course').ids.box_table.add_widget(table)
        self.dialog.dismiss()
        

    def show_dialog(self, title, text):
        """Display an error dialog."""
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDRaisedButton(
                    text="CLOSE",
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        dialog.open()
    
    def course_row_press(self, instance_table, instance_row):
        row_num = int(instance_row.index/len(instance_table.column_data))
        row_data = instance_table.row_data[row_num]
        print('ROW', row_data, self.sm.current_screen)
        self.screen = self.sm.current_screen
        if self.screen.name == 'main':
            col_input = [('ID', dp(30)), ('Name', dp(50)), ('T1', dp(20)), ('T2', dp(20)), ('T3', dp(20))]
            self.clas = row_data[-1]
            self.courseid = row_data[0]
            cursor.execute(f'SELECT s.id, fname, lname, term1, term2, term3 from gradingrpa.student as s join gradingrpa.course as c on s.class = c.class join gradingrpa.grade as g on c.id = g.courseid WHERE g.courseid = {self.courseid} and s.class = {self.clas}')
            grade = cursor.fetchall()
            row_input = [(item[0], item[1] + ' ' + item[2], item[3], item[4], item[5]) for item in grade]
            table = self.create_data_table(col_input,row_input)
            table.bind(on_row_press=self.course_row_press)
            self.sm.get_screen(self.sm.current).ids.box_table.clear_widgets()
            self.sm.get_screen('course').ids.box_table.clear_widgets()
            self.sm.get_screen('course').ids.nav_drawer.set_state('close')
            self.sm.get_screen('course').ids.box_table.add_widget(table)
            self.sm.current = 'course'
        elif self.screen.name == 'course':
            details = self.get_all_items_cond('grade', 'studentid', row_data[0], 'courseid', self.courseid)
            print(details)
            studentid = details[0][1]
            # gradedict.keys = self.sm.get_screen('grades').ids
            keys = list(self.sm.get_screen('grades').ids.keys())
            keys = [x for x in keys if keys.index(x) != 0]
            self.dialog = MDDialog(
            title='Change Grades',
            type="custom",
            content_cls=Grades(),
            buttons=[
                MDRaisedButton(
                    text="Submit",
                    on_release=lambda x: self.update_grade(keys, studentid, self.courseid)
                ),
                MDRaisedButton(
                    text="CLOSE",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                ],
            )
            self.dialog.open()
        print (row_data[0])
    def class_row_press(self, instance_table, instance_row):
        row_num = int(instance_row.index/len(instance_table.column_data))
        row_data = instance_table.row_data[row_num]
        clas = row_data[0]
        self.dialog = MDDialog(
        title= f'Generate Reports for Class {clas}?',
        type='custom',
        content_cls= Report(),
        buttons=[
            MDRaisedButton(
                text="Yes",
                on_release=lambda x: self.generate_reports(clas)
            ),
            MDRaisedButton(
                text="No",
                on_release=lambda x: self.dialog.dismiss()
            ),
            ],
        )
        self.dialog.open()
        print (row_data[0])

    def generate_reports(self, clas):
        cursor.execute(f'SELECT * FROM STUDENT WHERE class={clas}')
        students = [x  for x in cursor.fetchall()]
        for student in students:
            student_id = student[0]
            student_name = student[1] + ' ' + student[2]
            term = self.dialog.content_cls.ids.term.text.strip()
            # Create a new Document
            doc = Document()

            # Title
            doc.add_heading(f'Report Card for {student_name}', 0)

            # Add student details
            doc.add_paragraph(f'Student Name: {student_name}')
            
            # Add table for grades
            table = doc.add_table(rows=1, cols=2)
            table.style = 'Table Grid'
            
            # Set column names
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = 'Subject'
            hdr_cells[1].text = 'Grade'

            print(term)
            cursor.execute(f'SELECT {term}, courseid FROM grade WHERE studentid={student_id}')
            courses = [x for x in cursor.fetchall()]
            for course in courses:
                grade = f'{course[0]}'
                cursor.execute(f'SELECT name FROM course WHERE id={course[1]}')
                subject = cursor.fetchall()[0][0]
                print(grade,subject)
                

                # Add rows for each subject
 
                row_cells = table.add_row().cells
                row_cells[0].text = subject
                row_cells[1].text = grade

                # Add final remarks
            doc.add_paragraph('\nFinal Remarks:')
            doc.add_paragraph('Excellent progress in most subjects. Keep up the good work!')

            # Save the document
            doc.save(f'reports/{student_name}_report_card.docx')


if __name__ == "__main__":
    ReportGen().run()
