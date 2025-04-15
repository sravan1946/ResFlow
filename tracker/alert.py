from PyQt5.QtWidgets import QMessageBox
import time
from tracker.monitor import get_top_processes
from tracker.logger import log_alert

# Default values
DEFAULT_ALERT_THRESHOLD = 80  
DEFAULT_COOLDOWN_TIME = 20

# Global variables
last_alert_time = 0  
alert_threshold = DEFAULT_ALERT_THRESHOLD
COOLDOWN_TIME = DEFAULT_COOLDOWN_TIME

def set_alert_threshold(new_threshold):
    """Set the global alert threshold"""
    global alert_threshold
    alert_threshold = new_threshold

def set_cooldown_time(new_cooldown):
    global COOLDOWN_TIME
    COOLDOWN_TIME = new_cooldown

def show_alert(parent, usage_percent):
    global last_alert_time
    print(f"Checking alert: usage={usage_percent}, threshold={alert_threshold}")

    current_time = time.time()
    if usage_percent < alert_threshold or (current_time - last_alert_time) < COOLDOWN_TIME:
        return  

    last_alert_time = current_time  
    log_alert(usage_percent)
    top_processes = get_top_processes(3)  
    process_details = "\n".join([f"{p['name']} (PID: {p['pid']}) - {p['memory_percent']:.2f}%" for p in top_processes])

    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("High Memory Usage Alert")
    msg.setText(f"Memory usage is at {usage_percent}% (Threshold: {alert_threshold}%)!\n\nTop Memory Consuming Processes:\n{process_details}")
    msg.exec_()
    
