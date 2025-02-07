from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import MDList, ThreeLineIconListItem, IconLeftWidget, OneLineIconListItem
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

class Classes(Screen):
    pass
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

class Student(Screen):
    pass

class IconListItem(OneLineIconListItem):
    icon = StringProperty

class ReportGen(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.sm = Builder.load_file('reportgen.kv')
        self.menu = MDDropdownMenu()
        menu_items = [
            {
                "viewclass": "IconListItem",
                "icon": "git",
                "text": f"Term 1",
                "height": dp(56),
                "on_release": lambda x='term1': self.drop_handling(x)
            },
            {
                "viewclass": "IconListItem",
                "icon": "git",
                "text": f"Term 2",
                "height": dp(56),
                "on_release": lambda x='term2': self.drop_handling(x)
            },
            {
                "viewclass": "IconListItem",
                "icon": "git",
                "text": f"Term 3",
                "height": dp(56),
                "on_release": lambda x='term3': self.drop_handling(x)
            }
            ]
        self.menu = MDDropdownMenu(
            caller=self.sm.get_screen('report').ids.term,
            items=menu_items,
            position="center",
            width_mult=4,
        )
        self.menu.bind()
        return self.sm
    
    def drop_handling(self, term):
        print('HANDLE')
        self.menu.dismiss()
        self.dropdown_item.text = term
        

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
        if screen == 'courses':
            self.sm.get_screen('main').ids.scroll_main.clear_widgets()
            self.data_table = self.create_data_table('courses', [(item[0], item[1], item[-1]) for item in self.get_all_items('course', 'teacher', self.teacher)])
            # self.data_table.bind(on_row_press=self.course_row_press)
            self.sm.get_screen('main').ids.scroll_main.add_widget(self.data_table)
            self.sm.current = 'main'
        elif screen == 'classes':
            self.sm.get_screen('class').ids.scroll_main.clear_widgets()
            self.data_table = self.create_data_table('classes', [(item[0], item[1], ' ') for item in self.get_all_items('class', 'teacher', self.teacher)])
            # self.data_table.bind(on_row_press=self.class_row_press)
            self.sm.get_screen('class').ids.scroll_main.add_widget(self.data_table)
            self.sm.current = 'class'
            pass
        self.sm.get_screen('main').ids.nav_drawer.set_state('closed')

    def create_data_table(self, column_data, row_data):
        """Create an MDList widget."""
        mdlist = MDList()
        for thing in row_data:
            iteration = ThreeLineIconListItem(
                                            IconLeftWidget(icon='signal'),
                                            text= thing[1], 
                                            secondary_text= 'ID: ' + str(thing[0]),
                                            tertiary_text= str(thing[-1]),
                                            on_release= lambda x: self.on_row_press(x.text, x.secondary_text, x.tertiary_text),
                                            )
            mdlist.add_widget(iteration)
        return mdlist

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
    
    def on_row_press(self, name, id, third):
        id = id.split(':')[1].strip()
        self.third = third
        print(name, id, third)
        self.screen = self.sm.current_screen
        print(self.screen.name)
        if self.screen.name == 'main':
            self.courseid = id
            self.clas = third
            col_input = [('ID', dp(30)), ('Name', dp(50)), ('T1', dp(20)), ('T2', dp(20)), ('T3', dp(20))]
            cursor.execute(f"SELECT s.id, fname, lname, term1, term2, term3 from gradingrpa.student as s join gradingrpa.course as c on s.class = c.class join gradingrpa.grade as g on c.id = g.courseid WHERE g.courseid = '{self.courseid}' and s.class = '{self.clas}'")
            grade = cursor.fetchall()
            row_input = [(item[0], item[1] + ' ' + item[2], item[3], item[4], item[5], self.clas) for item in grade]
            print(row_input)
            table = self.create_data_table(col_input,row_input)
            self.sm.get_screen(self.sm.current).ids.scroll_main.clear_widgets()
            self.sm.get_screen('course').ids.scroll_course.clear_widgets()
            self.sm.get_screen('course').ids.nav_drawer.set_state('close')
            self.sm.get_screen('course').ids.scroll_course.add_widget(table)
            self.sm.current = 'course'
        elif self.screen.name == 'course':
            cursor.execute(f"SELECT s.id fname, lname, term1, term2, term3 FROM gradingrpa.student as s join gradingrpa.grade as g on s.id = g.studentid WHERE s.id= '{id}' AND g.courseid='{self.courseid}'")
            details = cursor.fetchall()
            print(details)
            self.studentid = details[0][0]
            self.studentname = details[0][1] + details[0][2]
            self.sm.get_screen('student').ids.studentname.text = self.studentname
            
            # # gradedict.keys = self.sm.get_screen('grades').ids
            # keys = list(self.sm.get_screen('grades').ids.keys())
            # keys = [x for x in keys if keys.index(x) != 0]
            # self.dialog = MDDialog(
            # title='Change Grades',
            # type="custom",
            # content_cls=Grades(),
            # buttons=[
            #     MDRaisedButton(
            #         text="Submit",
            #         on_release=lambda x: self.update_grade(keys, studentid, self.courseid)
            #     ),
            #     MDRaisedButton(
            #         text="CLOSE",
            #         on_release=lambda x: self.dialog.dismiss()
            #     ),
            #     ],
            # )
            # self.dialog.open()
            self.sm.current = 'student'
        elif self.screen.name == 'class':
            self.content_cls = Report()
            self.dropdown_item = self.content_cls.ids.term
            self.dropdown_item.text = 'Select Term'
            self.dialog = MDDialog(
            title= f'Generate Reports for Class {id}?',
            type='custom',
            content_cls= self.content_cls,
            buttons=[
                MDRaisedButton(
                    text="Yes",
                    on_release=lambda x: self.generate_reports(id)
                ),
                MDRaisedButton(
                    text="No",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                ],
            )
            self.dialog.open()
    def course_row_press(self, instance_table, instance_row):
        pass
    def class_row_press(self, instance_table, instance_row):
        pass

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
            doc.save(f'reports/{student_name}_{term}_report_card.docx')


if __name__ == "__main__":
    ReportGen().run()
