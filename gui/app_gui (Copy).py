import sys
import threading
import time
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QWidget, QSizePolicy, 
    QPushButton, QHBoxLayout, QFrame, QMainWindow
)
from PyQt5.QtCore import Qt, QTimer
import pyqtgraph as pg
from tracker.monitor import get_memory_usage, get_top_processes

# Set global pyqtgraph configuration
pg.setConfigOptions(antialias=True)

class MemoryTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Main setup
        self.setWindowTitle("ResFlow - Memory Tracker")
        self.setGeometry(100, 100, 800, 600)
        self.is_dark_mode = False
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create header with title and theme button
        header_layout = QHBoxLayout()
        title_label = QLabel("ResFlow Memory Monitor")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.theme_button = QPushButton("🌙 Dark Mode")
        self.theme_button.setFixedWidth(120)
        self.theme_button.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_button)
        self.main_layout.addLayout(header_layout)
        
        # Add a separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(line)
        
        # Memory usage display
        usage_layout = QHBoxLayout()
        self.memory_label = QLabel("Memory Usage: Fetching...")
        self.memory_label.setStyleSheet("font-size: 14px;")
        usage_layout.addWidget(self.memory_label)
        self.main_layout.addLayout(usage_layout)
        
        # Graph section
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground('w')
        self.graph_widget.setLabel('left', 'Memory Usage', units='%')
        self.graph_widget.setLabel('bottom', 'Time', units='s')
        self.graph_widget.showGrid(x=True, y=True)
        self.graph_widget.setYRange(0, 100)
        self.graph_widget.setTitle("Memory Usage Over Time")
        
        # Create plot line for memory usage
        self.memory_curve = self.graph_widget.plot([], [], pen=pg.mkPen(color='r', width=2))
        self.memory_data = np.array([])
        self.time_data = np.array([])
        self.elapsed_time = 0
        
        self.main_layout.addWidget(self.graph_widget)
        
        # Process information section
        process_frame = QFrame()
        process_frame.setFrameShape(QFrame.StyledPanel)
        process_layout = QVBoxLayout(process_frame)
        
        process_title = QLabel("Top Memory Consumers")
        process_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        process_layout.addWidget(process_title)
        
        self.process_label = QLabel("Fetching...")
        process_layout.addWidget(self.process_label)
        
        self.main_layout.addWidget(process_frame)
        
        # Initialize state
        self.alert_triggered = False
        self.apply_theme()
        self.start_tracking()

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()
        
    def apply_theme(self):
        if self.is_dark_mode:
            # Dark theme
            self.theme_button.setText("☀️ Light Mode")
            
            # App styling
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: #121212; color: #e0e0e0; }
                QLabel { color: #e0e0e0; }
                QPushButton { 
                    background-color: #2d2d2d; 
                    color: #e0e0e0; 
                    border: 1px solid #505050;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover { background-color: #3d3d3d; }
                QFrame { 
                    border: 1px solid #505050;
                    background-color: #1e1e1e;
                    border-radius: 4px;
                }
            """)
            
            # Graph styling
            self.graph_widget.setBackground('#121212')
            self.graph_widget.getAxis('bottom').setPen(pg.mkPen(color='#808080'))
            self.graph_widget.getAxis('left').setPen(pg.mkPen(color='#808080'))
            self.graph_widget.getAxis('bottom').setTextPen(pg.mkPen(color='#e0e0e0'))
            self.graph_widget.getAxis('left').setTextPen(pg.mkPen(color='#e0e0e0'))
            
            # Style grid lines
            self.graph_widget.getAxis('bottom').setGrid(255)
            self.graph_widget.getAxis('left').setGrid(255)
            self.graph_widget.showGrid(x=True, y=True, alpha=0.3)
        else:
            # Light theme
            self.theme_button.setText("🌙 Dark Mode")
            
            # App styling
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: #f5f5f5; color: #333333; }
                QLabel { color: #333333; }
                QPushButton { 
                    background-color: #e0e0e0; 
                    color: #333333; 
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover { background-color: #d0d0d0; }
                QFrame { 
                    border: 1px solid #cccccc;
                    background-color: white;
                    border-radius: 4px;
                }
            """)
            
            # Graph styling
            self.graph_widget.setBackground('w')
            self.graph_widget.getAxis('bottom').setPen(pg.mkPen(color='k'))
            self.graph_widget.getAxis('left').setPen(pg.mkPen(color='k'))
            self.graph_widget.getAxis('bottom').setTextPen(pg.mkPen(color='k'))
            self.graph_widget.getAxis('left').setTextPen(pg.mkPen(color='k'))
            
            # Style grid lines
            self.graph_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Update plot line color
        if len(self.memory_data) > 0:
            color = '#ff5050' if self.is_dark_mode else 'r'
            self.memory_curve.setPen(pg.mkPen(color=color, width=2))

    def start_tracking(self):
        # Use QTimer instead of threading for better Qt integration
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # Update every second
        
    #     # Start a separate thread for monitoring to avoid UI freezing
    #     self.monitor_thread = threading.Thread(target=self.monitor_system, daemon=True)
    #     self.monitor_thread.start()
    
    # def monitor_system(self):
    #     # This thread continuously monitors the system but doesn't update the UI directly
    #     while True:
    #         time.sleep(1)
    #         # Just keep the thread alive - actual updates happen in update_data

    def update_data(self):
        # Import alert functionality only when needed
        from tracker.alert import show_alert
        from tracker.logger import log_memory
        
        # Get current usage data
        usage = get_memory_usage()
        
        # Handle alerts
        if usage["percent"] > 80 and not self.alert_triggered:
            show_alert(self, usage["percent"])
            log_memory(f"ALERT: High memory usage detected at {usage['percent']}%")
            self.alert_triggered = True
        else:
            log_memory(f"Memory usage: {usage['percent']}%")
        
        self.alert_triggered = usage["percent"] > 80
        
        # Update memory label
        self.memory_label.setText(
            f"Memory Usage: {usage['percent']}% ({usage['used']}MB/{usage['total']}MB)"
        )
        
        # Get process information
        top_processes = get_top_processes(5)
        process_info = ""
        
        for i, p in enumerate(top_processes):
            process_info += f"<b>{i+1}.</b> {p['name']} (PID: {p['pid']}) - {p['memory_mb']}MB, CPU: {p['cpu_percent']}%<br>"
        
        self.process_label.setText(f"<html>{process_info}</html>")
        self.process_label.setTextFormat(Qt.RichText)
        
        # Update graph data
        self.elapsed_time += 1
        self.time_data = np.append(self.time_data, self.elapsed_time)
        self.memory_data = np.append(self.memory_data, usage["percent"])
        
        # Keep only the latest 60 data points (1 minute of data)
        if len(self.memory_data) > 60:
            self.memory_data = self.memory_data[-60:]
            self.time_data = self.time_data[-60:]
        
        # Update the plot
        self.memory_curve.setData(self.time_data, self.memory_data)
        
        # Add warning zone if memory usage is high
        if usage["percent"] > 70:
            color = '#ff5050' if self.is_dark_mode else 'r'
            self.memory_curve.setPen(pg.mkPen(color=color, width=2))
        else:
            color = '#4080ff' if self.is_dark_mode else 'b'
            self.memory_curve.setPen(pg.mkPen(color=color, width=2))

def start_app():
    app = QApplication(sys.argv)
    window = MemoryTrackerApp()
    window.show()
    sys.exit(app.exec_())