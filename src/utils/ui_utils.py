from PyQt5.QtWidgets import (QPushButton, QLabel, QLineEdit, 
                           QComboBox, QTableWidget, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Common styles
BUTTON_STYLE = """
    QPushButton {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 10px 20px;
        font-size: 14px;
        border-radius: 5px;
        min-height: 40px;
    }
    QPushButton:hover {
        background-color: #2980b9;
    }
    QPushButton:pressed {
        background-color: #2472a4;
    }
"""

INPUT_STYLE = """
    QLineEdit, QComboBox {
        padding: 10px;
        font-size: 14px;
        border: 1px solid #bdc3c7;
        border-radius: 5px;
        min-height: 40px;
    }
    QLineEdit:focus, QComboBox:focus {
        border: 2px solid #3498db;
    }
"""

TABLE_STYLE = """
    QTableWidget {
        border: none;
        gridline-color: #f0f0f0;
        font-size: 14px;
    }
    QHeaderView::section {
        background-color: #f8f9fa;
        padding: 10px;
        border: none;
        font-weight: bold;
    }
    QTableWidget::item {
        padding: 5px;
    }
"""

def create_styled_button(text: str, parent=None) -> QPushButton:
    """Create a styled button with consistent appearance"""
    button = QPushButton(text, parent)
    button.setStyleSheet(BUTTON_STYLE)
    return button

def create_styled_input(parent=None) -> QLineEdit:
    """Create a styled input field with consistent appearance"""
    input_field = QLineEdit(parent)
    input_field.setStyleSheet(INPUT_STYLE)
    return input_field

def create_styled_combo(parent=None) -> QComboBox:
    """Create a styled combo box with consistent appearance"""
    combo = QComboBox(parent)
    combo.setStyleSheet(INPUT_STYLE)
    return combo

def create_styled_table(columns: list, parent=None) -> QTableWidget:
    """Create a styled table with consistent appearance"""
    table = QTableWidget(parent)
    table.setColumnCount(len(columns))
    table.setHorizontalHeaderLabels(columns)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.setStyleSheet(TABLE_STYLE)
    return table

def create_styled_label(text: str, parent=None, font_size: int = 14) -> QLabel:
    """Create a styled label with consistent appearance"""
    label = QLabel(text, parent)
    label.setFont(QFont('Arial', font_size))
    return label

def setup_table_headers(table: QTableWidget):
    """Setup table headers with consistent styling"""
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Stretch)
    header.setStyleSheet("""
        QHeaderView::section {
            background-color: #f8f9fa;
            padding: 10px;
            border: none;
            font-weight: bold;
        }
    """) 