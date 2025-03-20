import psutil

def get_memory_usage():
    mem = psutil.virtual_memory()
    return {
        "total": round(mem.total / (1024 * 1024), 2),  # Convert bytes to MB
        "available": round(mem.available / (1024 * 1024), 2),
        "used": round(mem.used / (1024 * 1024), 2),
        "percent": mem.percent
    }

def get_top_processes(limit=5):
    processes = []
    
    for p in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent', 'memory_info']):
        try:
            if p.info['memory_percent'] < 0.1:  # Ignore processes using less than 0.1% memory
                continue
            processes.append({
                "pid": p.info['pid'],
                "name": p.info['name'],
                "memory_percent": round(p.info['memory_percent'], 2),
                "memory_mb": round(p.info['memory_info'].rss / (1024 * 1024), 2),  # Convert bytes to MB
                "cpu_percent": round(p.info['cpu_percent'], 2)
            })
        except psutil.NoSuchProcess:
            continue

    processes.sort(key=lambda x: (x['memory_percent'], x['cpu_percent']), reverse=True)
    
    return processes[:limit]
