import sys
import threading
import time
import matplotlib
matplotlib.use("Qt5Agg")  # Force Matplotlib to use Qt instead of TkAgg

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QSizePolicy, QPushButton


from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from tracker.monitor import get_memory_usage, get_top_processes
from tracker.alert import show_alert
from tracker.logger import log_memory

class MemoryTrackerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ResFlow - Memory Tracker")
        self.setGeometry(100, 100, 500, 400)
        self.is_dark_mode = False  # Initialize theme state
        self.memory_label = QLabel("Memory Usage: Fetching...", self)
        self.memory_label.setAlignment(Qt.AlignCenter)

        self.process_label = QLabel("Top Processes: Fetching...", self)
        self.process_label.setAlignment(Qt.AlignCenter)

        self.alert_triggered = False

        self.memory_data = []

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Theme Toggle Button
        self.theme_button = QPushButton("🌙 Dark Mode", self)
        self.theme_button.setFixedWidth(120)
        self.theme_button.setFixedHeight(30)
        self.theme_button.clicked.connect(self.toggle_theme)

        layout = QVBoxLayout()
        layout.addWidget(self.memory_label)
        layout.addWidget(self.process_label)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.set_graph_theme() 
        self.start_tracking()
    def toggle_theme(self):
        """Switch between dark and light mode."""
        if self.is_dark_mode:
            self.setStyleSheet("")
            self.theme_button.setText("🌙 Dark Mode")
        else:
            self.setStyleSheet("background-color: #121212; color: white;")
            self.theme_button.setText("☀️ Light Mode")

        self.is_dark_mode = not self.is_dark_mode
        self.set_graph_theme()  # Update graph colors

    def set_graph_theme(self):
        """Apply theme settings to the graph."""
        if self.is_dark_mode:
            self.figure.patch.set_facecolor("#121212")  # Dark background
            self.ax.set_facecolor("#121212")
            self.ax.spines["bottom"].set_color("white")
            self.ax.spines["left"].set_color("white")
            self.ax.xaxis.label.set_color("white")
            self.ax.yaxis.label.set_color("white")
            self.ax.tick_params(axis="x", colors="white")
            self.ax.tick_params(axis="y", colors="white")
            self.ax.grid(color="gray", linestyle="--", linewidth=0.5)
            self.ax.title.set_color("white")
        else:
            self.figure.patch.set_facecolor("white")  # Light background
            self.ax.set_facecolor("white")
            self.ax.spines["bottom"].set_color("black")
            self.ax.spines["left"].set_color("black")
            self.ax.xaxis.label.set_color("black")
            self.ax.yaxis.label.set_color("black")
            self.ax.tick_params(axis="x", colors="black")
            self.ax.tick_params(axis="y", colors="black")
            self.ax.grid(color="gray", linestyle="--", linewidth=0.5)
            
        self.canvas.draw()  # Refresh canvas

    def start_tracking(self):
        tracking_thread = threading.Thread(target=self.track_memory, daemon=True)
        tracking_thread.start()

        self.ani = animation.FuncAnimation(self.figure, self.update_graph, interval=300)

    def track_memory(self):
        while True:
            usage = get_memory_usage()

            if usage["percent"] > 80 and not self.alert_triggered:
                show_alert(self, usage["percent"])
                log_memory(f"ALERT: High memory usage detected at {usage['percent']}%")
                self.alert_triggered = True  
            else:
                log_memory(f"Memory usage: {usage['percent']}%")  

            self.alert_triggered = usage["percent"] > 80  

            self.memory_label.setText(f"Memory Usage: {usage['percent']}% ({usage['used']}MB/{usage['total']}MB)")
            
            top_processes = get_top_processes(3)
            process_info = "\n".join(
                [f"{p['name']} (PID: {p['pid']}) - {p['memory_mb']}MB, CPU: {p['cpu_percent']}%" for p in top_processes]
            )
            self.process_label.setText(f"Top Processes:\n{process_info}")

            self.memory_data.append(usage["percent"])
            if len(self.memory_data) > 50:
                self.memory_data.pop(0)

            time.sleep(1)

    def update_graph(self, frame):
        self.ax.clear()
        self.ax.plot(self.memory_data, label="Memory Usage (%)", color="red")
        self.ax.set_ylim(0, 100)
        self.ax.set_ylabel("Usage (%)")
        self.ax.set_title("Memory Usage Over Time")
        self.ax.legend()

        self.set_graph_theme()  # Apply the theme first

        self.ax.grid(color="gray", linestyle="--", linewidth=0.5)  # Reapply the grid AFTER theme

        self.canvas.draw()


def start_app():
    app = QApplication(sys.argv)
    window = MemoryTrackerApp()
    window.show()
    sys.exit(app.exec_())
