import psutil
import time
from datetime import datetime
import subprocess

# File that contains dynamic thresholds
THRESHOLD_FILE = "/home/z004ymtp/dynamic_thresholds.txt"
ALERT_LOG_FILE = "/home/z004ymtp/Logs/system_usage.txt"

# Default thresholds (in case the threshold file is missing)
CPU_THRESHOLD = 30  # %
MEMORY_THRESHOLD = 75  # %
NETWORK_THRESHOLD = 2  # MBps

# Get current date and time
def get_current_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Get CPU usage percentage
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

# Get memory usage percentage
def get_memory_usage():
    memory = psutil.virtual_memory()
    return memory.percent

# Get network usage in MBps
def get_network_usage():
    net1 = psutil.net_io_counters()
    time.sleep(1)
    net2 = psutil.net_io_counters()
    sent_bytes = (net2.bytes_sent - net1.bytes_sent) / (1024 * 1024)
    recv_bytes = (net2.bytes_recv - net1.bytes_recv) / (1024 * 1024)
    return sent_bytes + recv_bytes

# Check if admin is logged in
def is_admin_logged_in():
    try:
        output = subprocess.check_output(["w"], universal_newlines=True)
        for line in output.splitlines():
            if 'z004ymtp' in line and 'pts' in line:
                return True
        return False
    except subprocess.CalledProcessError:
        print("Error checking logged-in users.")
        return False

# Get top CPU-consuming process
def get_top_cpu_process():
    top_process = max(psutil.process_iter(['pid', 'name', 'username', 'cpu_percent']),
                      key=lambda p: p.info['cpu_percent'], default=None)
    return top_process.info if top_process else None

# Get top memory-consuming process
def get_top_memory_process():
    top_process = max(psutil.process_iter(['pid', 'name', 'username', 'memory_percent']),
                      key=lambda p: p.info['memory_percent'], default=None)
    return top_process.info if top_process else None

# Get top network-consuming process (based on read_bytes + write_bytes)
def get_top_network_process():
    top_process = max(
        psutil.process_iter(['pid', 'name', 'username', 'io_counters']),
        key=lambda p: (p.info['io_counters'].read_bytes + p.info['io_counters'].write_bytes) if p.info['io_counters'] else 0,
        default=None
    )
    return top_process.info if top_process else None


# Log alerts with the latest alert on top
def log_alert(message):
    timestamp = get_current_time()
    with open(ALERT_LOG_FILE, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(f"{timestamp} - ALERT: {message}\n" + content)

# Load dynamic thresholds from the file
def load_thresholds():
    global CPU_THRESHOLD, MEMORY_THRESHOLD, NETWORK_THRESHOLD
    try:
        with open(THRESHOLD_FILE, 'r') as f:
            for line in f:
                if "CPU_THRESHOLD" in line:
                    CPU_THRESHOLD = float(line.split('=')[1].strip())
                elif "MEMORY_THRESHOLD" in line:
                    MEMORY_THRESHOLD = float(line.split('=')[1].strip())
                elif "NETWORK_THRESHOLD" in line:
                    NETWORK_THRESHOLD = float(line.split('=')[1].strip())
    except FileNotFoundError:
        print(f"{get_current_time()} - Threshold file not found. Using default thresholds.")

# Check if current resource usage exceeds thresholds
def check_thresholds():
    load_thresholds()  # Load the latest thresholds before checking
    
    cpu_usage = get_cpu_usage()
    memory_usage = get_memory_usage()
    network_usage = get_network_usage()
    
    if (cpu_usage > CPU_THRESHOLD and memory_usage > MEMORY_THRESHOLD) or \
       (cpu_usage > CPU_THRESHOLD and network_usage > NETWORK_THRESHOLD) or \
       (memory_usage > MEMORY_THRESHOLD and network_usage > NETWORK_THRESHOLD):
        
        # Check if admin is logged in
        admin_logged_in = is_admin_logged_in()
        admin_status = "Admin is logged in." if admin_logged_in else "Admin is NOT logged in."
        
        # Get top resource-using processes
        top_cpu = get_top_cpu_process()
        top_memory = get_top_memory_process()
        top_network = get_top_network_process()
        
        # Format detailed alert message
        alert_message = (
            f"High usage detected! CPU: {cpu_usage}%, Memory: {memory_usage}%, Network: {network_usage} MB/s - {admin_status}\n"
            f"Top CPU-consuming process: {top_cpu['name']} (User: {top_cpu['username']}, Usage: {top_cpu['cpu_percent']}%)\n"
            f"Top Memory-consuming process: {top_memory['name']} (User: {top_memory['username']}, Usage: {top_memory['memory_percent']}%)\n"
            f"Top Network-consuming process: {top_network['name']} (User: {top_network['username']}, Bytes: "
            f"{top_network['io_counters'].read_bytes + top_network['io_counters'].write_bytes if top_network['io_counters'] else 0})"
        )        
        log_alert(alert_message)
        print(alert_message)
    else:
        print(f"System usage normal. CPU: {cpu_usage}%, Memory: {memory_usage}%, Network: {network_usage} MB/s")

# Main loop to check resource usage every minute
def main():
    while True:
        check_thresholds()
        time.sleep(10)

if __name__ == "__main__":
    main()