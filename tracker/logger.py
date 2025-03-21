import logging
import os
from logging.handlers import RotatingFileHandler
from tracker.monitor import get_top_processes

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Memory usage log
memory_log_file = os.path.join(log_dir, "memory_log.txt")
memory_handler = RotatingFileHandler(memory_log_file, maxBytes=5 * 1024 * 1024, backupCount=3)

# Alert log
alert_log_file = os.path.join(log_dir, "alert_log.txt")
alert_handler = RotatingFileHandler(alert_log_file, maxBytes=2 * 1024 * 1024, backupCount=2)

log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

memory_handler.setFormatter(log_formatter)
alert_handler.setFormatter(log_formatter)

memory_logger = logging.getLogger("MemoryLogger")
memory_logger.setLevel(logging.INFO)
memory_logger.addHandler(memory_handler)

alert_logger = logging.getLogger("AlertLogger")
alert_logger.setLevel(logging.INFO)
alert_logger.addHandler(alert_handler)

def log_memory(usage_percent):
    top_processes = get_top_processes(3)
    process_details = "; ".join([f"{p['name']} (PID: {p['pid']}) - {p['memory_percent']:.2f}%" for p in top_processes])
    
    memory_logger.info(f"Memory Usage: {usage_percent}%; Top Processes: {process_details}")

def log_alert(usage_percent):
    # Get the top process consuming the most memory
    top_process = get_top_processes(1)[0]
    top_process_details = f"{top_process['name']} (PID: {top_process['pid']}) - {top_process['memory_percent']:.2f}%"

    # Log the alert with the highest memory-consuming process
    alert_logger.warning(
        f"ALERT: High Memory Usage at {usage_percent}%; Highest Memory Process: {top_process_details}"
    )
