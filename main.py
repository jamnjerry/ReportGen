from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.uix.textinput import TextInput
import mysql.connector as connector
from datetime import datetime
from logging import ERROR
from collections import deque

conn = connector.connect(
    host="127.0.0.1",         # Replace with your MySQL server's hostname or IP address
    user="root",              # Replace with your MySQL username
    password="Highpeople11",      # Replace with your MySQL password
    database="gradingrpa",  # Database name
    auth_plugin='mysql_native_password'
)

cursor = conn.cursor()

class MainScreen(Screen):
    pass

class CourseScreen(Screen):
    pass

class Grades(Screen):
    pass

class ReportGen(MDApp):
    teacher = 1
    def build(self):
        self.inventory = []  # List to hold inventory data
        self.theme_cls.primary_palette = "Cyan"
        self.sm = Builder.load_file('reportgen.kv')
        self.data_table = self.create_data_table([
                ("ID", dp(30)),
                ("Course Name", dp(70)),
                ('Class ID', dp(30)),
            ], [(item[0], item[1], item[-1]) for item in self.get_all_items('course', 'teacher', self.teacher)])
        self.sm.get_screen('main').ids.box_table.add_widget(self.data_table)
        return self.sm

    def create_data_table(self, column_data, row_data):
        """Create an MDDataTable widget."""
        table = MDDataTable(
            size_hint=(1, 1),
            check=True,
            use_pagination=True,
            elevation=0,
            background_color_header="yellow",
            rows_num=5,
            column_data=column_data,
            row_data= row_data,
        )
        table.bind(on_row_press=self.on_row_press)
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
    
    def on_row_press(self, instance_table, instance_row):
        row_num = int(instance_row.index/len(instance_table.column_data))
        row_data = instance_table.row_data[row_num]
        print('ROW', row_data)
        self.screen = self.sm.current_screen
        if self.screen.name == 'main':
            col_input = [('ID', dp(30)), ('Name', dp(50)), ('T1', dp(20)), ('T2', dp(20)), ('T3', dp(20))]
            self.clas = row_data[-1]
            self.courseid = row_data[0]
            cursor.execute(f'SELECT s.id, fname, lname, term1, term2, term3 from gradingrpa.student as s join gradingrpa.course as c on s.class = c.class join gradingrpa.grade as g on c.id = g.courseid WHERE g.courseid = {self.courseid} and s.class = {self.clas}')
            grade = cursor.fetchall()
            row_input = [(item[0], item[1] + ' ' + item[2], item[3], item[4], item[5]) for item in grade]
            table = self.create_data_table(col_input,row_input)
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
            title=self.name,
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

if __name__ == "__main__":
    ReportGen().run()
