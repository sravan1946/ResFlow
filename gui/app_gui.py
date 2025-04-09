import signal
import sys
import os
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QWidget, QPushButton,
    QHBoxLayout, QFrame, QMainWindow
)
from PyQt5.QtCore import Qt, QTimer
import pyqtgraph as pg
from tracker.monitor import get_memory_usage, get_top_processes
from PyQt5.QtWidgets import QSizePolicy, QScrollArea
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor

# Set global pyqtgraph configuration
pg.setConfigOptions(antialias=True)

class MemoryTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Main setup
        self.setWindowTitle("ResFlow - Memory Tracker")
        self.setGeometry(100, 100, 900, 700)
        self.is_dark_mode = False
        
        # Create central widget and layout
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.central_widget = QWidget()
        scroll_area.setWidget(self.central_widget)
        self.setCentralWidget(scroll_area)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create header with title and theme button
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.add_shadow(header_frame)

        title_label = QLabel("ResFlow Memory Monitor")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.theme_button = QPushButton("🌙 Dark Mode")
        self.theme_button.setFixedWidth(140)
        self.theme_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        self.theme_button.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_button)

        self.main_layout.addWidget(header_frame)

        # Memory usage display
        usage_frame = QFrame()
        usage_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.add_shadow(usage_frame)

        usage_layout = QHBoxLayout(usage_frame)
        self.memory_label = QLabel("Memory Usage: Fetching...")
        self.memory_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.memory_label.setAlignment(Qt.AlignCenter)  # Centered text
        usage_layout.addWidget(self.memory_label)

        self.main_layout.addWidget(usage_frame)

        # Graph widget
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.graph_widget.setBackground('w')
        self.graph_widget.setLabel('left', 'Memory Usage', units='%')
        self.graph_widget.setLabel('bottom', 'Time', units='s')
        self.graph_widget.showGrid(x=True, y=True, alpha=0.3)
        self.graph_widget.setYRange(0, 100)
        self.graph_widget.enableAutoRange(axis='y', enable=True)
        self.graph_widget.setTitle("Memory Usage Over Time", size="14pt")
        self.graph_widget.setMinimumHeight(400)
        self.graph_widget.setMaximumHeight(400)

        viewbox = self.graph_widget.getViewBox()
        viewbox.setLimits(
            xMin=0, xMax=None, minXRange=5, maxXRange=60,
            yMin=0, yMax=120, minYRange=5, maxYRange=120
        )
        viewbox.setMouseEnabled(x=False, y=False)

        # Create plot line for memory usage with fill
        self.memory_curve = self.graph_widget.plot([], [], pen=pg.mkPen(color='r', width=3))
        
        # Add filled area under the curve
        self.fill_curve = pg.PlotDataItem([], [], 
            fillLevel=0, 
            brush=pg.mkBrush(color=(255, 0, 0, 100)),  # Semi-transparent red fill
            pen=None
        )
        self.graph_widget.addItem(self.fill_curve)

        self.memory_data = np.array([])
        self.time_data = np.array([])
        self.elapsed_time = 0

        self.main_layout.addWidget(self.graph_widget)

        # Process information section
        process_frame = QFrame()
        process_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.add_shadow(process_frame)

        process_layout = QVBoxLayout(process_frame)

        process_title = QLabel("Top Memory Consumers")
        process_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        process_layout.addWidget(process_title)

        self.process_cards = QVBoxLayout()
        process_layout.addLayout(self.process_cards)

        self.main_layout.addWidget(process_frame)

        # Initialize state
        self.alert_triggered = False
        self.apply_theme()
        self.start_tracking()

    def add_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(3)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 60))
        widget.setGraphicsEffect(shadow)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def apply_theme(self):
        if self.is_dark_mode:
            self.theme_button.setText("☀️ Light Mode")
            
            # Main application style
            self.setStyleSheet("""
                QMainWindow, QScrollArea { background-color: #121212; }
                QWidget { color: #e0e0e0; }
                QLabel { color: #ffffff; }
                
                QPushButton {
                    background-color: #3700B3;
                    color: white;
                    font-weight: bold;
                    border-radius: 6px;
                    padding: 8px 12px;
                }
                QPushButton:hover {
                    background-color: #6200EE;
                }
                
                QScrollBar:vertical {
                    border: none;
                    background: #1e1e1e;
                    width: 10px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #3700B3;
                    min-height: 20px;
                    border-radius: 5px;
                }
            """)
            
            # Set graph background
            self.graph_widget.setBackground('#1e1e1e')
            self.graph_widget.getAxis('left').setPen(pg.mkPen(color='#6200EE'))
            self.graph_widget.getAxis('bottom').setPen(pg.mkPen(color='#6200EE'))
            
            # Update all frames to dark theme
            for i in range(self.main_layout.count()):
                item = self.main_layout.itemAt(i)
                if item.widget() and isinstance(item.widget(), QFrame):
                    item.widget().setStyleSheet("""
                        background-color: #1e1e1e;
                        border-radius: 10px;
                        padding: 15px;
                        border: 1px solid #333333;
                    """)
        else:
            self.theme_button.setText("🌙 Dark Mode")
            
            # Main application style
            self.setStyleSheet("""
                QMainWindow, QScrollArea { background-color: #f5f5f5; }
                QWidget { color: #333333; }
                QLabel { color: #333333; }
                
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    font-weight: bold;
                    border-radius: 6px;
                    padding: 8px 12px;
                }
                QPushButton:hover {
                    background-color: #005a9e;
                }
                
                QScrollBar:vertical {
                    border: none;
                    background: #f0f0f0;
                    width: 10px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #0078d4;
                    min-height: 20px;
                    border-radius: 5px;
                }
            """)
            
            # Set graph background
            self.graph_widget.setBackground('#ffffff')
            self.graph_widget.getAxis('left').setPen(pg.mkPen(color='#0078d4'))
            self.graph_widget.getAxis('bottom').setPen(pg.mkPen(color='#0078d4'))
            
            # Update all frames to light theme
            for i in range(self.main_layout.count()):
                item = self.main_layout.itemAt(i)
                if item.widget() and isinstance(item.widget(), QFrame):
                    item.widget().setStyleSheet("""
                        background-color: white;
                        border-radius: 10px;
                        padding: 15px;
                        border: 1px solid #e0e0e0;
                    """)

    def start_tracking(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)

    def update_process_cards(self, processes):
        # Clear existing cards
        for i in reversed(range(self.process_cards.count())):
            widget = self.process_cards.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for process in processes:
            card = QFrame()
            if self.is_dark_mode:
                card.setStyleSheet("""
                    QFrame {
                        background-color: #1e1e1e;
                        border-radius: 10px;
                        padding: 10px;
                        border: 1px solid #333333;
                    }
                    QFrame:hover {
                        background-color: #333333;
                    }
                """)
            else:
                card.setStyleSheet("""
                    QFrame {
                        background-color: white;
                        border-radius: 10px;
                        padding: 10px;
                        border: 1px solid #e0e0e0;
                    }
                    QFrame:hover {
                        background-color: #f0f0f0;
                    }
                """)
            self.add_shadow(card)

            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(8, 6, 8, 6)
            card_layout.setSpacing(10)

            # Process name and details in a single line
            process_info = f"<b>{process['name']}</b> (PID: {process['pid']}) - {process['memory_mb']}MB, CPU: {process['cpu_percent']}%"
            process_label = QLabel(process_info)
            process_label.setStyleSheet("font-size: 14px; background-color: transparent; border: none;")
            card_layout.addWidget(process_label)

            # Create kill button with improved styling but shorter text
            kill_button = QPushButton("Kill")
            kill_button.setFixedWidth(70)
            
            if self.is_dark_mode:
                kill_button.setStyleSheet("""
                    QPushButton {
                        background-color: #CF6679;
                        color: white;
                        font-weight: bold;
                        border-radius: 6px;
                        padding: 6px;
                    }
                    QPushButton:hover {
                        background-color: #E57373;
                    }
                """)
            else:
                kill_button.setStyleSheet("""
                    QPushButton {
                        background-color: #F44336;
                        color: white;
                        font-weight: bold;
                        border-radius: 6px;
                        padding: 6px;
                    }
                    QPushButton:hover {
                        background-color: #E53935;
                    }
                """)
                
            kill_button.clicked.connect(lambda _, pid=process["pid"]: self.kill_process(pid))
            card_layout.addWidget(kill_button)

            self.process_cards.addWidget(card)
            
    def kill_process(self, pid):
        try:
            os.kill(pid, 9)
            print(f"Process with PID {pid} killed successfully.")
        except BaseException as e:
            print(f"Error killing process with PID {pid}: {e}")

    def update_data(self):
        from tracker.alert import show_alert
        from tracker.logger import log_memory

        usage = get_memory_usage()
        if usage["percent"] > 80 and not self.alert_triggered:
            show_alert(self, usage["percent"])
            log_memory(f"ALERT: High memory usage detected at {usage['percent']}%")
            self.alert_triggered = True
        else:
            self.alert_triggered = False

        # Update memory label
        self.memory_label.setText(
            f"Memory Usage: {usage['percent']}% ({usage['used']}MB/{usage['total']}MB)"
        )

        # Get process information
        top_processes = get_top_processes(5)
        self.update_process_cards(top_processes)

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
        self.fill_curve.setData(self.time_data, self.memory_data)

        # Add warning zone if memory usage is high
        if usage["percent"] > 70:
            fill_color = (255, 80, 80, 100) if self.is_dark_mode else (255, 0, 0, 100)
            line_color = '#ff5050' if self.is_dark_mode else 'r'
            self.memory_curve.setPen(pg.mkPen(color=line_color, width=3))
            self.fill_curve.setBrush(pg.mkBrush(color=fill_color))
        else:
            fill_color = (64, 128, 255, 100) if self.is_dark_mode else (0, 0, 255, 100)
            line_color = '#4080ff' if self.is_dark_mode else 'b'
            self.memory_curve.setPen(pg.mkPen(color=line_color, width=3))
            self.fill_curve.setBrush(pg.mkBrush(color=fill_color))

def start_app():
    app = QApplication(sys.argv)
    window = MemoryTrackerApp()
    window.show()
    # Set up signal handling for Ctrl+C
    def signal_handler(sig, frame):
        print("Closing application...")
        app.quit()
    
    # Register the signal handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Use a timer to process Python signals (required for Qt apps)
    timer = QTimer()
    timer.start(500)  # 500ms
    timer.timeout.connect(lambda: None)  # Dummy function to process events

    sys.exit(app.exec_())

if __name__ == "__main__":
    start_app()