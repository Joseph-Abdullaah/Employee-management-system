from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QFrame, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime
from src.utils.ui_utils import (create_styled_label, create_styled_table, 
                            setup_table_headers)

class DashboardTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()
        
        # Setup auto-refresh timer (every 5 seconds)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(5000)  # 5 seconds

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Stats section
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        # Create stat widgets
        self.emp_label = self.create_stat_widget('👥', 'Total Employees', '0')
        self.att_label = self.create_stat_widget('📈', 'Attendance Rate', '0%')
        self.gender_label = self.create_stat_widget('👫', 'Gender Distribution', '0%')

        stats_layout.addWidget(self.emp_label)
        stats_layout.addWidget(self.att_label)
        stats_layout.addWidget(self.gender_label)
        layout.addLayout(stats_layout)

        # Chart section
        chart_frame = QFrame()
        chart_frame.setStyleSheet('background-color: white; border-radius: 10px;')
        chart_layout = QVBoxLayout(chart_frame)

        # Chart title
        chart_title = create_styled_label('Attendance Overview', font_size=16)
        chart_title.setStyleSheet('font-weight: bold;')
        chart_layout.addWidget(chart_title)

        self.figure = plt.figure(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        layout.addWidget(chart_frame)

        # Recent activities section
        activities_frame = QFrame()
        activities_frame.setStyleSheet('background-color: white; border-radius: 10px;')
        activities_layout = QVBoxLayout(activities_frame)

        activities_title = create_styled_label('Recent Activities', font_size=16)
        activities_title.setStyleSheet('font-weight: bold;')
        activities_layout.addWidget(activities_title)

        self.activities_table = create_styled_table(['Time', 'Activity'])
        setup_table_headers(self.activities_table)
        activities_layout.addWidget(self.activities_table)
        layout.addWidget(activities_frame)

        self.setLayout(layout)
        self.refresh_data()

    def create_stat_widget(self, icon: str, title: str, value: str) -> QFrame:
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        layout = QVBoxLayout(widget)
        
        # Icon and title
        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet('font-size: 24px;')
        title_label = create_styled_label(title)
        title_label.setStyleSheet('color: #7f8c8d;')
        header.addWidget(icon_label)
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)
        
        # Value
        value_label = create_styled_label(value, font_size=24)
        value_label.setStyleSheet('font-weight: bold; color: #2c3e50;')
        value_label.setObjectName('value_label')
        layout.addWidget(value_label)
        
        return widget

    def refresh_data(self):
        # Update stats
        stats = self.db.get_dashboard_stats()
        
        # Update employee count
        self.emp_label.findChild(QLabel, 'value_label').setText(
            str(stats['total_employees']))
        
        # Update attendance rate
        self.att_label.findChild(QLabel, 'value_label').setText(
            f"{stats['attendance_rate']:.1f}%")
        
        # Update gender distribution
        gender_stats = stats['gender_stats']
        gender_text = f"Male: {gender_stats.get('Male', 0):.1f}%\n"
        gender_text += f"Female: {gender_stats.get('Female', 0):.1f}%"
        self.gender_label.findChild(QLabel, 'value_label').setText(gender_text)
        
        # Update chart
        self.update_chart()
        
        # Update activities
        self.update_activities()

    def update_chart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Get attendance data
        stats = self.db.get_attendance_stats()
        dates = [stat[0] for stat in stats]
        rates = [stat[2]/stat[1]*100 if stat[1] > 0 else 0 for stat in stats]

        # Create gradient bars
        bars = ax.bar(dates, rates)
        for bar in bars:
            bar.set_color('#3498db')

        ax.set_ylabel('Attendance Rate (%)')
        ax.set_xlabel('Date')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.xticks(rotation=45)
        plt.tight_layout()
        self.canvas.draw()

    def update_activities(self):
        activities = self.db.get_recent_activities()
        self.activities_table.setRowCount(len(activities))
        
        for i, (_, description, timestamp) in enumerate(activities):
            time_str = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
            
            time_item = QTableWidgetItem(time_str)
            activity_item = QTableWidgetItem(description)
            
            time_item.setTextAlignment(Qt.AlignCenter)
            
            self.activities_table.setItem(i, 0, time_item)
            self.activities_table.setItem(i, 1, activity_item) 