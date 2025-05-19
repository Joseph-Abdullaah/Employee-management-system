from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QMessageBox, QCheckBox, QTableWidgetItem)
from PyQt5.QtCore import pyqtSignal
from datetime import datetime
from src.utils.ui_utils import (create_styled_button, create_styled_input, 
                            create_styled_combo, create_styled_table, 
                            create_styled_label, setup_table_headers)

class AttendanceTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Date Display
        date_layout = QHBoxLayout()
        today = datetime.now().strftime('%Y-%m-%d')
        date_label = create_styled_label(f'Date: {today}', font_size=14)
        date_layout.addWidget(date_label)
        
        save_btn = create_styled_button('💾 Save Attendance')
        save_btn.clicked.connect(self.save_attendance)
        date_layout.addWidget(save_btn)
        date_layout.addStretch()
        
        layout.addLayout(date_layout)

        # Attendance List
        list_label = create_styled_label('📋 Daily Attendance List', font_size=16)
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
        present_ids = [a[1] for a in attendance if a[3]]  # employee_ids who are present

        for i, emp in enumerate(employees):
            # ID
            self.table.setItem(i, 0, QTableWidgetItem(str(emp[0])))
            # Name
            self.table.setItem(i, 1, QTableWidgetItem(emp[1]))
            # Checkbox
            checkbox = QCheckBox()
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-size: 14px;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                }
            """)
            checkbox.setChecked(emp[0] in present_ids)
            self.table.setCellWidget(i, 2, checkbox)

    def save_attendance(self):
        today = datetime.now().date()
        saved_count = 0

        for row in range(self.table.rowCount()):
            employee_id = int(self.table.item(row, 0).text())
            is_present = self.table.cellWidget(row, 2).isChecked()
            self.db.mark_attendance(employee_id, today, is_present)
            if is_present:
                saved_count += 1

        self.refresh_table()
        QMessageBox.information(self, 'Success', 
                               f'Attendance saved successfully!\n{saved_count} employees marked as present.') 