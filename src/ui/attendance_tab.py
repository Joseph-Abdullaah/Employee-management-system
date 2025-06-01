from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QMessageBox, QCheckBox, QTableWidgetItem)
from PyQt5.QtCore import pyqtSignal, Qt
from datetime import datetime
from src.utils.ui_utils import (create_styled_button, create_styled_input, 
                            create_styled_combo, create_styled_table, 
                            create_styled_label, setup_table_headers)

class AttendanceTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.attendance_states = {}  # Store attendance states
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)  # Reduced margins
        layout.setSpacing(15)  # Reduced spacing

        # Date Display
        date_layout = QHBoxLayout()
        today = datetime.now().strftime('%Y-%m-%d')
        date_label = create_styled_label(f'Date: {today}', font_size=12)
        date_layout.addWidget(date_label)
        
        save_btn = create_styled_button('Save Attendance')
        save_btn.clicked.connect(self.save_attendance)
        date_layout.addWidget(save_btn)
        date_layout.addStretch()
        
        layout.addLayout(date_layout)

        # Attendance List
        list_label = create_styled_label('Daily Attendance List', font_size=14)
        list_label.setStyleSheet('font-weight: bold;')
        layout.addWidget(list_label)

        self.table = create_styled_table(['ID', 'Employee Name', 'Present?'])
        setup_table_headers(self.table)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.refresh_table()

    def refresh_table(self):
        """Refresh the attendance table with current employees"""
        employees = self.db.get_all_employees()
        self.table.setRowCount(len(employees))
        
        today = datetime.now().date()
        attendance = self.db.get_attendance_by_date(today)
        
        # Update attendance states from database
        for a in attendance:
            self.attendance_states[a[1]] = a[3]  # employee_id -> present status

        for i, emp in enumerate(employees):
            # ID
            self.table.setItem(i, 0, QTableWidgetItem(str(emp[0])))
            # Name
            self.table.setItem(i, 1, QTableWidgetItem(emp[1]))
            
            # Checkbox
            checkbox = QCheckBox()
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-size: 12px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
            """)
            
            # Set initial state from our stored states
            is_checked = self.attendance_states.get(emp[0], False)
            checkbox.setChecked(is_checked)
            
            # Connect state change signal
            checkbox.stateChanged.connect(
                lambda state, emp_id=emp[0]: self.on_checkbox_changed(emp_id, state)
            )
            
            self.table.setCellWidget(i, 2, checkbox)

    def on_checkbox_changed(self, employee_id, state):
        """Handle checkbox state changes"""
        self.attendance_states[employee_id] = (state == Qt.Checked)

    def save_attendance(self):
        today = datetime.now().date()
        saved_count = 0

        for employee_id, is_present in self.attendance_states.items():
            self.db.mark_attendance(employee_id, today, is_present)
            if is_present:
                saved_count += 1

        QMessageBox.information(self, 'Success', 
                               f'Attendance saved successfully!\n{saved_count} employees marked as present.') 