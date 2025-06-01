from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QRadioButton, QButtonGroup, QMessageBox, QTableWidgetItem)
from PyQt5.QtCore import pyqtSignal, QRegExp
from PyQt5.QtGui import QRegExpValidator
from src.utils.ui_utils import (create_styled_button, create_styled_input, 
                            create_styled_combo, create_styled_table, 
                            create_styled_label, setup_table_headers)

class EmployeeTab(QWidget):
    # Signal to notify other components of employee changes
    employee_updated = pyqtSignal()

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)  # Reduced margins
        layout.setSpacing(15)  # Reduced spacing

        # Form Layout
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)  # Reduced spacing

        # Employee ID (read-only)
        id_layout = QHBoxLayout()
        id_layout.addWidget(create_styled_label('ID:', font_size=12))
        self.id_input = create_styled_input()
        self.id_input.setReadOnly(True)
        self.id_input.setPlaceholderText('Auto-generated')
        id_layout.addWidget(self.id_input)
        form_layout.addLayout(id_layout)

        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(create_styled_label('Name:', font_size=12))
        self.name_input = create_styled_input()
        self.name_input.setMaxLength(50)
        
        # Set up name validation using QRegExp
        name_regex = QRegExp(r'^[A-Za-z\s]*$')
        name_validator = QRegExpValidator(name_regex)
        self.name_input.setValidator(name_validator)
        self.name_input.setPlaceholderText('Enter name (letters only)')
        
        name_layout.addWidget(self.name_input)
        form_layout.addLayout(name_layout)

        # Gender
        gender_layout = QHBoxLayout()
        gender_layout.addWidget(create_styled_label('Gender:', font_size=12))
        self.gender_group = QButtonGroup()
        
        male_radio = QRadioButton('Male')
        female_radio = QRadioButton('Female')
        
        # Style radio buttons
        for radio in [male_radio, female_radio]:
            radio.setStyleSheet("""
                QRadioButton {
                    font-size: 12px;
                    padding: 3px;
                }
                QRadioButton::indicator {
                    width: 16px;
                    height: 16px;
                }
            """)
        
        self.gender_group.addButton(male_radio, 1)
        self.gender_group.addButton(female_radio, 2)
        
        gender_layout.addWidget(male_radio)
        gender_layout.addWidget(female_radio)
        form_layout.addLayout(gender_layout)

        # Email
        email_layout = QHBoxLayout()
        email_layout.addWidget(create_styled_label('Email:', font_size=12))
        self.email_input = create_styled_input()
        email_layout.addWidget(self.email_input)
        form_layout.addLayout(email_layout)

        # Department
        dept_layout = QHBoxLayout()
        dept_layout.addWidget(create_styled_label('Department:', font_size=12))
        self.dept_input = create_styled_combo()
        self.dept_input.addItems(['HR', 'Finance', 'IT', 'Marketing', 'Operations'])
        dept_layout.addWidget(self.dept_input)
        form_layout.addLayout(dept_layout)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = create_styled_button('Save')
        save_btn.clicked.connect(self.save_employee)
        clear_btn = create_styled_button('Clear Form')
        clear_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(clear_btn)
        form_layout.addLayout(button_layout)

        layout.addLayout(form_layout)

        # Employee List
        list_label = create_styled_label('Employee List', font_size=14)
        list_label.setStyleSheet('font-weight: bold;')
        layout.addWidget(list_label)

        self.table = create_styled_table(['ID', 'Name', 'Gender', 'Email', 'Department'])
        setup_table_headers(self.table)
        layout.addWidget(self.table)

        # Action Buttons
        action_layout = QHBoxLayout()
        edit_btn = create_styled_button('Edit Selected')
        edit_btn.clicked.connect(self.edit_selected)
        delete_btn = create_styled_button('Delete Selected')
        delete_btn.clicked.connect(self.delete_selected)
        refresh_btn = create_styled_button('Refresh List')
        refresh_btn.clicked.connect(self.refresh_table)
        
        action_layout.addWidget(edit_btn)
        action_layout.addWidget(delete_btn)
        action_layout.addWidget(refresh_btn)
        layout.addLayout(action_layout)

        self.setLayout(layout)
        self.refresh_table()

    def validate_name(self, text):
        """Validate that name contains only letters and spaces"""
        # Remove any non-letter characters (except spaces)
        cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text)
        if cleaned_text != text:
            # If text was modified, update the input
            self.name_input.setText(cleaned_text)
            # Move cursor to end
            self.name_input.setCursorPosition(len(cleaned_text))

    def save_employee(self):
        name = self.name_input.text().strip()  # Remove leading/trailing spaces
        email = self.email_input.text()
        department = self.dept_input.currentText()
        
        gender_id = self.gender_group.checkedId()
        gender = {1: 'Male', 2: 'Female'}.get(gender_id)

        if not all([name, email, department, gender]):
            QMessageBox.warning(self, 'Error', 'All fields are required!')
            return

        # Additional name validation using QRegExp
        name_regex = QRegExp(r'^[A-Za-z\s]+$')
        if not name_regex.exactMatch(name):
            QMessageBox.warning(self, 'Error', 'Name can only contain letters and spaces!')
            return

        if self.id_input.text():  # Update existing employee
            success = self.db.update_employee(
                int(self.id_input.text()),
                name, gender, email, department
            )
        else:  # Add new employee
            success = self.db.add_employee(name, gender, email, department)

        if success:
            self.clear_form()
            self.refresh_table()
            self.employee_updated.emit()  # Notify other components
            QMessageBox.information(self, 'Success', 'Employee saved successfully!')
        else:
            QMessageBox.warning(self, 'Error', 'Email already exists!')

    def clear_form(self):
        self.id_input.clear()
        self.name_input.clear()
        self.email_input.clear()
        self.dept_input.setCurrentIndex(0)
        if self.gender_group.checkedButton():
            self.gender_group.checkedButton().setChecked(False)

    def refresh_table(self):
        employees = self.db.get_all_employees()
        self.table.setRowCount(len(employees))
        for i, emp in enumerate(employees):
            for j, value in enumerate(emp):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

    def edit_selected(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Error', 'Please select an employee to edit!')
            return

        self.id_input.setText(self.table.item(current_row, 0).text())
        self.name_input.setText(self.table.item(current_row, 1).text())
        gender = self.table.item(current_row, 2).text()
        gender_map = {'Male': 1, 'Female': 2}
        if gender in gender_map:
            self.gender_group.button(gender_map[gender]).setChecked(True)
        self.email_input.setText(self.table.item(current_row, 3).text())
        self.dept_input.setCurrentText(self.table.item(current_row, 4).text())

    def delete_selected(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Error', 'Please select an employee to delete!')
            return

        employee_id = int(self.table.item(current_row, 0).text())
        reply = QMessageBox.question(self, 'Confirm Delete',
                                   'Are you sure you want to delete this employee?',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.db.delete_employee(employee_id)
            self.refresh_table()
            self.employee_updated.emit()  # Notify other components
            QMessageBox.information(self, 'Success', 'Employee deleted successfully!') 