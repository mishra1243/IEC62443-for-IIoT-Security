import psutil
import time
from datetime import datetime

# Define the log file location
ALERT_LOG_FILE = "/home/z004ymtp/Logs/logs.txt"

# Define the thresholds
CPU_THRESHOLD = 20  # CPU usage percentage
MEMORY_THRESHOLD = 60  # Memory usage percentage
NETWORK_THRESHOLD = 4  # Network usage in MBps

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
    time.sleep(1)  # Monitor network usage over 1 second
    net2 = psutil.net_io_counters()
    sent_bytes = (net2.bytes_sent - net1.bytes_sent) / (1024 * 1024)  # Convert to MB
    recv_bytes = (net2.bytes_recv - net1.bytes_recv) / (1024 * 1024)  # Convert to MB
    return sent_bytes + recv_bytes  # Total network traffic in MBps

# Log alerts with the latest alert on top
def log_alert(message):
    timestamp = get_current_time()
    with open(ALERT_LOG_FILE, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(f"{timestamp} - ALERT: {message}\n" + content)

# Check if two or more thresholds are exceeded and log an alert
def check_thresholds():
    cpu_usage = get_cpu_usage()
    memory_usage = get_memory_usage()
    network_usage = get_network_usage()

    print(f"CPU: {cpu_usage}%, Memory: {memory_usage}%, Network: {network_usage} MB/s")

    # Count how many thresholds are exceeded
    count = 0
    if cpu_usage > CPU_THRESHOLD:
        count += 1
    if memory_usage > MEMORY_THRESHOLD:
        count += 1
    if network_usage > NETWORK_THRESHOLD:
        count += 1

    # If two or more thresholds are exceeded, log an alert
    if count >= 2:
        log_alert(f"High resource usage detected! CPU: {cpu_usage}%, Memory: {memory_usage}%, Network: {network_usage} MB/s")

# Main loop to monitor system resources every 10 seconds
def main():
    # Create the log file if it doesn't exist
    with open(ALERT_LOG_FILE, 'a') as f:
        pass

    # Continuously monitor system resources
    while True:
        check_thresholds()
        time.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    main()