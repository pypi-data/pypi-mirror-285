import psutil


def get_process_info():
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        yield proc.info


def kill_process(pid):
    p = psutil.Process(pid)
    p.terminate()


def suggest_kill_process(threshold=20):
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        if proc.info['memory_percent'] > threshold:
            print(f"Suggest killing process {proc.info['name']} (PID: {proc.info['pid']}) using {proc.info['memory_percent']}% of memory.")
