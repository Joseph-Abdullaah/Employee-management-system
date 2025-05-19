import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('employee_management.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Employees table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gender TEXT NOT NULL CHECK(gender IN ('Male', 'Female')),
                email TEXT UNIQUE NOT NULL,
                department TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Shifts table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS shifts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                shift_type TEXT NOT NULL,
                assigned_date DATE DEFAULT CURRENT_DATE,
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')

        # Attendance table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                date DATE NOT NULL,
                present BOOLEAN NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')

        # Activity log table for real-time updates
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                description TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()

    def close(self):
        self.conn.close()

    def log_activity(self, action_type: str, description: str):
        """Log an activity for real-time updates"""
        self.cursor.execute('''
            INSERT INTO activity_log (action_type, description)
            VALUES (?, ?)
        ''', (action_type, description))
        self.conn.commit()

    # Employee Management Methods
    def add_employee(self, name: str, gender: str, email: str, department: str) -> bool:
        try:
            self.cursor.execute('''
                INSERT INTO employees (name, gender, email, department)
                VALUES (?, ?, ?, ?)
            ''', (name, gender, email, department))
            self.conn.commit()
            self.log_activity('employee_added', f'New employee added: {name}')
            return True
        except sqlite3.IntegrityError:
            return False

    def get_all_employees(self) -> List[tuple]:
        self.cursor.execute('SELECT * FROM employees')
        return self.cursor.fetchall()

    def get_employee_by_id(self, employee_id: int) -> Optional[tuple]:
        self.cursor.execute('SELECT * FROM employees WHERE id = ?', (employee_id,))
        return self.cursor.fetchone()

    def update_employee(self, id: int, name: str, gender: str, email: str, department: str) -> bool:
        try:
            self.cursor.execute('''
                UPDATE employees 
                SET name=?, gender=?, email=?, department=?
                WHERE id=?
            ''', (name, gender, email, department, id))
            self.conn.commit()
            self.log_activity('employee_updated', f'Employee updated: {name}')
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_employee(self, id: int):
        employee = self.get_employee_by_id(id)
        if employee:
            self.cursor.execute('DELETE FROM employees WHERE id=?', (id,))
            self.conn.commit()
            self.log_activity('employee_deleted', f'Employee deleted: {employee[1]}')

    def get_gender_stats(self) -> Dict[str, float]:
        """Get gender distribution statistics"""
        self.cursor.execute('''
            SELECT gender, COUNT(*) as count
            FROM employees
            GROUP BY gender
        ''')
        results = self.cursor.fetchall()
        total = sum(count for _, count in results)
        return {gender: (count/total)*100 if total > 0 else 0 
                for gender, count in results}

    # Shift Management Methods
    def assign_shift(self, employee_id: int, shift_type: str):
        employee = self.get_employee_by_id(employee_id)
        if employee:
            self.cursor.execute('''
                INSERT INTO shifts (employee_id, shift_type)
                VALUES (?, ?)
            ''', (employee_id, shift_type))
            self.conn.commit()
            self.log_activity('shift_assigned', 
                            f'Shift {shift_type} assigned to {employee[1]}')

    def get_all_shifts(self) -> List[tuple]:
        self.cursor.execute('''
            SELECT s.id, e.name, s.shift_type, s.assigned_date
            FROM shifts s 
            JOIN employees e ON s.employee_id = e.id
            ORDER BY s.assigned_date DESC
        ''')
        return self.cursor.fetchall()

    # Attendance Management Methods
    def mark_attendance(self, employee_id: int, date: str, present: bool):
        employee = self.get_employee_by_id(employee_id)
        if employee:
            self.cursor.execute('''
                INSERT OR REPLACE INTO attendance (employee_id, date, present)
                VALUES (?, ?, ?)
            ''', (employee_id, date, present))
            self.conn.commit()
            status = "present" if present else "absent"
            self.log_activity('attendance_marked', 
                            f'Marked {employee[1]} as {status}')

    def get_attendance_by_date(self, date: str) -> List[tuple]:
        self.cursor.execute('''
            SELECT a.id, e.id, e.name, a.present
            FROM attendance a 
            JOIN employees e ON a.employee_id = e.id 
            WHERE a.date=?
        ''', (date,))
        return self.cursor.fetchall()

    def get_attendance_stats(self) -> List[tuple]:
        self.cursor.execute('''
            SELECT date, 
                   COUNT(*) as total,
                   SUM(CASE WHEN present THEN 1 ELSE 0 END) as present_count
            FROM attendance
            GROUP BY date
            ORDER BY date DESC
            LIMIT 30
        ''')
        return self.cursor.fetchall()

    def get_dashboard_stats(self) -> Dict[str, Any]:
        # Get total employees
        self.cursor.execute('SELECT COUNT(*) FROM employees')
        total_employees = self.cursor.fetchone()[0]

        # Get attendance rate for today
        today = datetime.now().date()
        self.cursor.execute('''
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN present THEN 1 ELSE 0 END) as present_count
            FROM attendance
            WHERE date=?
        ''', (today,))
        attendance_data = self.cursor.fetchone()
        attendance_rate = 0
        if attendance_data and attendance_data[0] > 0:
            attendance_rate = (attendance_data[1] / attendance_data[0]) * 100

        # Get gender stats
        gender_stats = self.get_gender_stats()

        return {
            'total_employees': total_employees,
            'attendance_rate': attendance_rate,
            'gender_stats': gender_stats
        }

    def get_recent_activities(self, limit: int = 10) -> List[tuple]:
        """Get recent activities for the dashboard"""
        self.cursor.execute('''
            SELECT action_type, description, timestamp
            FROM activity_log
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall() 