import psutil
import time
from datetime import datetime

# File to store the dynamic thresholds
THRESHOLD_FILE = "/home/z004ymtp/dynamic_thresholds.txt"

# Variables to store accumulated values
cpu_sum = 0
memory_sum = 0
network_sum = 0
iterations = 0

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

# Write new dynamic thresholds to a file
def write_thresholds(cpu_avg, memory_avg, network_avg):
    with open(THRESHOLD_FILE, 'w') as f:
        f.write(f"CPU_THRESHOLD={cpu_avg}\n")
        f.write(f"MEMORY_THRESHOLD={memory_avg}\n")
        f.write(f"NETWORK_THRESHOLD={network_avg}\n")

# Calculate and log averages every hour
def calculate_average_and_update_threshold():
    global cpu_sum, memory_sum, network_sum, iterations
    
    # Calculate the averages
    cpu_avg = cpu_sum / iterations
    memory_avg = memory_sum / iterations
    network_avg = network_sum / iterations
    
    # Add a safety margin, e.g., increase the threshold by 10%
    cpu_threshold = cpu_avg * 1.10
    memory_threshold = memory_avg * 1.10
    network_threshold = network_avg * 1.10
    
    # Write the new thresholds to the file
    write_thresholds(cpu_threshold, memory_threshold, network_threshold)
    
    print(f"{get_current_time()} - New thresholds set: CPU: {cpu_threshold}%, Memory: {memory_threshold}%, Network: {network_threshold} MB/s")
    
    # Reset the sums and iterations for the next hour
    cpu_sum = 0
    memory_sum = 0
    network_sum = 0
    iterations = 0

# Main loop to collect data and update thresholds every hour
def main():
    global cpu_sum, memory_sum, network_sum, iterations
    
    start_time = time.time()  # Track when the hour starts
    
    while True:
        # Collect system data
        cpu_usage = get_cpu_usage()
        memory_usage = get_memory_usage()
        network_usage = get_network_usage()
        
        # Accumulate data for averaging
        cpu_sum += cpu_usage
        memory_sum += memory_usage
        network_sum += network_usage
        iterations += 1
        
        # Check if an hour has passed (3600 seconds)
        if time.time() - start_time >= 3600:
            calculate_average_and_update_threshold()
            start_time = time.time()  # Reset the hour timer
        
        time.sleep(60)  # Collect data every 60 seconds

if __name__ == "__main__":
    main()