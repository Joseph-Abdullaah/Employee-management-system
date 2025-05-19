import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import EmployeeManagementSystem
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EmployeeManagementSystem()
    window.show()
    sys.exit(app.exec_()) 