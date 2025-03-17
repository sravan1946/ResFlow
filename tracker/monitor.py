import psutil

def get_memory_usage():
    mem = psutil.virtual_memory()
    return mem.percent

def get_top_processes(limit=5):
    processes = []
    for p in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            processes.append(p.info)
        except psutil.NoSuchProcess:
            continue
    processes.sort(key=lambda x: x['memory_percent'], reverse=True)
    return processes[:limit]
