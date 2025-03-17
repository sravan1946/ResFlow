import logging
import os

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "memory_log.txt")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - Memory Usage: %(message)s"
)

def log_memory(usage_percent):
    logging.info(f"{usage_percent}%")
