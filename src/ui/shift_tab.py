from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QMessageBox, QTableWidgetItem)
from PyQt5.QtCore import pyqtSignal
from src.utils.ui_utils import (create_styled_button, create_styled_combo, 
                            create_styled_table, create_styled_label, 
                            setup_table_headers)

class ShiftTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Form Layout
        form_layout = QHBoxLayout()
        form_layout.setSpacing(15)

        # Employee Selection
        employee_label = create_styled_label('Employee:')
        self.employee_combo = create_styled_combo()
        form_layout.addWidget(employee_label)
        form_layout.addWidget(self.employee_combo)

        # Shift Type Selection
        shift_label = create_styled_label('Shift Type:')
        self.shift_combo = create_styled_combo()
        self.shift_combo.addItems(['Morning', 'Evening', 'Night'])
        form_layout.addWidget(shift_label)
        form_layout.addWidget(self.shift_combo)

        # Assign Button
        assign_btn = create_styled_button('📌 Assign Shift')
        assign_btn.clicked.connect(self.assign_shift)
        form_layout.addWidget(assign_btn)

        layout.addLayout(form_layout)

        # Shift List
        list_label = create_styled_label('📋 Assigned Shifts', font_size=16)
        list_label.setStyleSheet('font-weight: bold;')
        layout.addWidget(list_label)

        self.table = create_styled_table(['ID', 'Employee Name', 'Shift Type', 'Date'])
        setup_table_headers(self.table)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.refresh_employee_list()
        self.refresh_table()

    def refresh_employee_list(self):
        """Refresh the employee dropdown list"""
        self.employee_combo.clear()
        employees = self.db.get_all_employees()
        for emp in employees:
            self.employee_combo.addItem(emp[1], emp[0])  # name, id

    def assign_shift(self):
        employee_id = self.employee_combo.currentData()
        shift_type = self.shift_combo.currentText()

        if not employee_id:
            QMessageBox.warning(self, 'Error', 'Please select an employee!')
            return

        self.db.assign_shift(employee_id, shift_type)
        self.refresh_table()
        QMessageBox.information(self, 'Success', 'Shift assigned successfully!')

    def refresh_table(self):
        """Refresh the shifts table"""
        shifts = self.db.get_all_shifts()
        self.table.setRowCount(len(shifts))
        for i, shift in enumerate(shifts):
            for j, value in enumerate(shift):
                self.table.setItem(i, j, QTableWidgetItem(str(value))) 