from PyQt5.QtWidgets import QMessageBox
import time
from tracker.monitor import get_top_processes
from tracker.logging import log_alert  # Import alert logging function

ALERT_THRESHOLD = 80  
COOLDOWN_TIME = 60  

last_alert_time = 0  

def show_alert(parent, usage_percent):
    global last_alert_time

    current_time = time.time()
    if usage_percent < ALERT_THRESHOLD or (current_time - last_alert_time) < COOLDOWN_TIME:
        return  

    last_alert_time = current_time  

    log_alert(usage_percent)  # Log the alert

    top_processes = get_top_processes(3)  
    process_details = "\n".join([f"{p['name']} (PID: {p['pid']}) - {p['memory_percent']:.2f}%" for p in top_processes])

    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("High Memory Usage Alert")
    msg.setText(f"Memory usage is at {usage_percent}%!\n\nTop Memory Consuming Processes:\n{process_details}")
    msg.exec_()
