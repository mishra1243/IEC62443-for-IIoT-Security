#!/usr/bin/python3
import subprocess
import re
import os

# Define path to the log file
LOG_FILE = "/home/z004ymtp/Logs/network_logs.txt"

# Ensure the log file exists
if not os.path.exists(LOG_FILE):
    open(LOG_FILE, 'a').close()

# Command to follow kernel logs
cmd = ["journalctl", "-k", "-f"]

# Compile regex pattern to identify dropped connection attempts
pattern = re.compile(r"Dropped connection attempt")

# Start subprocess to monitor logs
with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
    try:
        # Continuously read stdout
        while True:
            line = process.stdout.readline().strip()
            if line:
                # Check if line matches the pattern
                if pattern.search(line):
                    # Update log file
                    with open(LOG_FILE, 'r+') as f:
                        content = f.read()
                        f.seek(0, 0)
                        f.write(line + "\n" + content)
    except KeyboardInterrupt:
        print("Stopping log monitoring.")
