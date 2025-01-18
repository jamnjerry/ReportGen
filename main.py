from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
import mysql.connector as connector
from datetime import datetime

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

class ReportGen(MDApp):
    teacher = 1
    def build(self):
        self.inventory = []  # List to hold inventory data
        self.theme_cls.primary_palette = "Cyan"
        self.sm = Builder.load_file('reportgen.kv')
        self.data_table = self.create_data_table()
        self.data_table.bind(on_row_press=self.on_row_press)
        self.sm.get_screen('main').ids.box_main.add_widget(self.data_table)
        return self.sm

    def create_data_table(self):
        """Create an MDDataTable widget."""
        return MDDataTable(
            size_hint=(1, 1),
            check=True,
            use_pagination=True,
            elevation=0,
            background_color_header="yellow",
            rows_num=5,
            column_data=[
                ("ID", dp(50)),
                ("Course Name", dp(200)),
            ],
            row_data= [(item[0], item[1]) for item in self.get_all_items()],
        )

    def get_all_items(self):
        cursor.execute(f"SELECT * FROM course WHERE teacher={self.teacher}")
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
        print('course')

if __name__ == "__main__":
    ReportGen().run()
