import logging
import os
from logging.handlers import RotatingFileHandler
from tracker.monitor import get_top_processes

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "memory_log.txt")

log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)  
handler.setFormatter(log_formatter)

logger = logging.getLogger("MemoryLogger")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

def log_memory(usage_percent):
    top_processes = get_top_processes(3)
    process_details = "; ".join([f"{p['name']} (PID: {p['pid']}) - {p['memory_percent']:.2f}%" for p in top_processes])
    
    logger.info(f"Memory Usage: {usage_percent}%; Top Processes: {process_details}")

