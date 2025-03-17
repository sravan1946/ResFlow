import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QTextEdit, QSplitter
from PyQt5.QtCore import QTimer, Qt
import pyqtgraph as pg

from tracker.monitor import get_memory_usage, get_top_processes
from tracker.logger import log_memory
from tracker.alert import show_alert

class MemoryTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Memory Tracker with Graph and Process Viewer")
        self.resize(800, 600)

        # Layout
        layout = QVBoxLayout(self)

        # Memory Usage Label
        self.label = QLabel("Memory Usage:", self)
        layout.addWidget(self.label)

        # Graph
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setYRange(0, 100, padding=0)
        self.data = []
        self.plot = self.graph_widget.plot()
        layout.addWidget(self.graph_widget)

        # Process List
        self.process_text = QTextEdit()
        self.process_text.setReadOnly(True)
        layout.addWidget(self.process_text)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.track_memory)
        self.timer.start(1000)

        self.alert_triggered = False
        self.show()

    def track_memory(self):
        usage = get_memory_usage()
        self.label.setText(f"Memory Usage: {usage}%")
        log_memory(usage)

        # Update Graph
        self.data.append(usage)
        if len(self.data) > 100:
            self.data.pop(0)
        self.plot.setData(self.data)

        # Alert
        if usage > 80 and not self.alert_triggered:
            show_alert(self, usage)
            self.alert_triggered = True
        elif usage <= 80:
            self.alert_triggered = False

        # Update Top Processes
        processes = get_top_processes()
        proc_text = "Top Processes by Memory Usage:\n\n"
        for p in processes:
            proc_text += f"PID: {p['pid']} | Name: {p['name']} | Mem: {p['memory_percent']:.2f}%\n"
        self.process_text.setText(proc_text)

def start_app():
    app = QApplication(sys.argv)
    window = MemoryTrackerApp()
    sys.exit(app.exec_())
