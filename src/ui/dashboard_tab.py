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
        layout.setContentsMargins(15, 15, 15, 15)  # Reduced margins
        layout.setSpacing(15)  # Reduced spacing

        # Top section - Stats
        stats_frame = QFrame()
        stats_frame.setStyleSheet('background-color: white; border-radius: 8px;')
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(15)

        # Create stat widgets with reduced size
        self.emp_label = self.create_stat_widget('Total Employees', '0')
        self.att_label = self.create_stat_widget('Attendance Rate', '0%')
        self.gender_label = self.create_stat_widget('Gender Distribution', '0%')

        stats_layout.addWidget(self.emp_label)
        stats_layout.addWidget(self.att_label)
        stats_layout.addWidget(self.gender_label)
        layout.addWidget(stats_frame)

        # Middle section - Chart
        chart_frame = QFrame()
        chart_frame.setStyleSheet('background-color: white; border-radius: 8px;')
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(10, 10, 10, 10)

        chart_title = create_styled_label('Attendance Overview', font_size=14)
        chart_title.setStyleSheet('font-weight: bold;')
        chart_layout.addWidget(chart_title)

        self.figure = plt.figure(figsize=(8, 3))  # Reduced figure size
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        layout.addWidget(chart_frame)

        # Bottom section - Activities
        activities_frame = QFrame()
        activities_frame.setStyleSheet('background-color: white; border-radius: 8px;')
        activities_layout = QVBoxLayout(activities_frame)
        activities_layout.setContentsMargins(10, 10, 10, 10)

        activities_title = create_styled_label('Recent Activities', font_size=14)
        activities_title.setStyleSheet('font-weight: bold;')
        activities_layout.addWidget(activities_title)

        self.activities_table = create_styled_table(['Time', 'Activity'])
        setup_table_headers(self.activities_table)
        activities_layout.addWidget(self.activities_table)
        layout.addWidget(activities_frame)

        # Set equal stretch for all sections
        layout.setStretch(0, 1)  # Stats section
        layout.setStretch(1, 1)  # Chart section
        layout.setStretch(2, 1)  # Activities section

        self.setLayout(layout)
        self.refresh_data()

    def create_stat_widget(self, title: str, value: str) -> QFrame:
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        
        # Title
        title_label = create_styled_label(title, font_size=12)
        title_label.setStyleSheet('color: #7f8c8d;')
        layout.addWidget(title_label)
        
        # Value
        value_label = create_styled_label(value, font_size=18)  # Reduced font size
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
        
        if not stats:
            # If no data, show empty chart
            ax.text(0.5, 0.5, 'No attendance data available', 
                   horizontalalignment='center', verticalalignment='center')
            plt.tight_layout()
            self.canvas.draw()
            return

        # Convert dates to datetime objects and rates to float
        dates = []
        rates = []
        for stat in stats:
            try:
                date_str = stat[0]
                if date_str:  # Only process if date is not None
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                    total = float(stat[1])
                    present = float(stat[2])
                    rate = (present / total * 100) if total > 0 else 0
                    dates.append(date)
                    rates.append(rate)
            except (ValueError, TypeError) as e:
                print(f"Error processing date {date_str}: {e}")
                continue

        if not dates:  # If no valid dates after processing
            ax.text(0.5, 0.5, 'No valid attendance data available', 
                   horizontalalignment='center', verticalalignment='center')
            plt.tight_layout()
            self.canvas.draw()
            return

        # Create gradient bars
        bars = ax.bar(dates, rates)
        for bar in bars:
            bar.set_color('#3498db')

        # Format x-axis dates
        ax.set_ylabel('Attendance Rate (%)')
        ax.set_xlabel('Date')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Format date labels
        plt.gcf().autofmt_xdate()  # Rotate and align the tick labels
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
        
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