import sys
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QStackedWidget,
                           QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from src.database.database import Database
from src.ui.dashboard_tab import DashboardTab
from src.ui.employee_tab import EmployeeTab
from src.ui.shift_tab import ShiftTab
from src.ui.attendance_tab import AttendanceTab
from src.utils.ui_utils import create_styled_button, create_styled_label

class SidebarButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(50)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                border-radius: 5px;
                color: white;
                font-size: 14px;
                padding: 10px;
                text-align: left;
                border: none;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:checked {
                background-color: #3498db;
            }
        """)

class EmployeeManagementSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.initUI()
        
        # Setup auto-refresh timer (every 5 seconds)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_all)
        self.timer.start(5000)  # 5 seconds

    def initUI(self):
        self.setWindowTitle('Employee Management System')
        self.setGeometry(100, 100, 1400, 800)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        # Create sidebar
        sidebar = QFrame()
        sidebar.setStyleSheet('background-color: #2c3e50;')
        sidebar.setMaximumWidth(200)
        sidebar.setMinimumWidth(200)
        sidebar_layout = QVBoxLayout()
        
        # Add date/time display to sidebar
        self.datetime_label = create_styled_label('', font_size=12)
        self.datetime_label.setStyleSheet('color: white; padding: 10px;')
        self.update_datetime()
        sidebar_layout.addWidget(self.datetime_label)
        
        # Setup datetime update timer
        datetime_timer = QTimer(self)
        datetime_timer.timeout.connect(self.update_datetime)
        datetime_timer.start(1000)  # Update every second

        # Create navigation buttons
        self.nav_buttons = []
        pages = [
            ('📊 Dashboard', DashboardTab),
            ('👥 Employees', EmployeeTab),
            ('🕒 Shifts', ShiftTab),
            ('📋 Attendance', AttendanceTab)
        ]

        for text, widget in pages:
            btn = SidebarButton(text)
            btn.clicked.connect(lambda checked, w=widget: self.change_page(w))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()
        sidebar.setLayout(sidebar_layout)

        # Create stacked widget for pages
        self.stack = QStackedWidget()
        
        # Initialize all pages
        self.pages = {}
        for _, widget in pages:
            page = widget(self.db)
            self.pages[widget] = page
            self.stack.addWidget(page)

        # Connect employee updates to other components
        if EmployeeTab in self.pages:
            self.pages[EmployeeTab].employee_updated.connect(self.on_employee_updated)

        # Set default page
        self.nav_buttons[0].setChecked(True)

        # Add widgets to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

    def change_page(self, widget_class):
        # Uncheck all buttons except the clicked one
        for btn in self.nav_buttons:
            if btn.text() != self.sender().text():
                btn.setChecked(False)
        
        # Show the selected page
        self.stack.setCurrentWidget(self.pages[widget_class])

    def update_datetime(self):
        current_time = datetime.now().strftime('%Y-%m-%d\n%H:%M:%S')
        self.datetime_label.setText(current_time)

    def refresh_all(self):
        # Refresh all pages
        for page in self.pages.values():
            if hasattr(page, 'refresh_table'):
                page.refresh_table()
            if hasattr(page, 'refresh_data'):
                page.refresh_data()

    def on_employee_updated(self):
        """Handle employee updates across all components"""
        # Refresh shift tab employee list
        if ShiftTab in self.pages:
            self.pages[ShiftTab].refresh_employee_list()
        
        # Refresh attendance tab
        if AttendanceTab in self.pages:
            self.pages[AttendanceTab].refresh_table()
        
        # Refresh dashboard
        if DashboardTab in self.pages:
            self.pages[DashboardTab].refresh_data()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EmployeeManagementSystem()
    window.show()
    sys.exit(app.exec_()) 