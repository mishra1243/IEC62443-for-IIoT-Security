import subprocess
import re
import time
import os
import shutil

# File path to store the logs
LOG_FILE = '/home/z004ymtp/Logs/auth_log.txt'

# Dictionary to track failed login attempts
failed_attempts = {}

# Define thresholds
MAX_FAILED_ATTEMPTS = 3
DISABLE_DURATION = 60  # in seconds, adjust as needed

# Mapping for username aliases
username_aliases = {
    'z004ymtp': 'admin',
    'local': 'Local'
}

# Helper function to remove SSH keys temporarily and log the action
def disable_user_ssh(user):
    alias_user = username_aliases.get(user, user)  # Get alias or default to real username
    print(f"Disabling SSH keys for user {alias_user}")
    auth_keys_path = f"/home/{user}/.ssh/authorized_keys"
    if os.path.exists(auth_keys_path):
        backup_path = f"/home/{user}/.ssh/authorized_keys.bak"
        shutil.copy(auth_keys_path, backup_path)  # Backup existing keys
        os.remove(auth_keys_path)  # Remove the authorized_keys file
        print(f"SSH keys for user {alias_user} have been disabled and logged.")

        # Log the action in the log file
        log_entry = f"{time.ctime()} - User {alias_user} has been temporarily disabled due to exceeding maximum failed login attempts.\n"
        log_entry_at_top(log_entry)
        
        time.sleep(DISABLE_DURATION)
        
        # Restore the SSH keys
        shutil.move(backup_path, auth_keys_path)
        print(f"SSH keys for user {alias_user} have been re-enabled.")
        enable = f"{time.ctime()} - SSH keys have been re-enabled for {alias_user}.\n"
        log_entry_at_top(enable)
    else:
        print(f"User {alias_user} does not have SSH keys or the ~/.ssh/authorized_keys file is missing.")

# Function to log entries at the top of the file
def log_entry_at_top(log_entry):
    # Read the existing file content
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as log_file:
            content = log_file.read()
    else:
        content = ''
    
    # Prepend the new log entry
    new_content = log_entry + content
    
    # Write back the updated content
    with open(LOG_FILE, 'w') as log_file:
        log_file.write(new_content)

# Process journalctl logs
proc = subprocess.Popen(['journalctl', '-u', 'ssh', '-f'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

while True:
    line = proc.stdout.readline().decode('utf-8').strip()
    
    if 'Disconnected' in line:
        # Extract the username and IP from the "Disconnected" line
        user_ip_match = re.search(r'authenticating user (\S+) (\d+\.\d+\.\d+\.\d+)', line)
        
        if user_ip_match:
            user = user_ip_match.group(1)
            ip = user_ip_match.group(2)
            
            # Use alias if available, else use the original username
            alias_user = username_aliases.get(user, user)
            
            if user not in failed_attempts:
                failed_attempts[user] = 0
            
            failed_attempts[user] += 1
            
            # Log the failed attempt
            log_entry = f"{time.ctime()} - Failed login attempt for user {alias_user} from IP {ip}\n"
            log_entry_at_top(log_entry)
            print(log_entry.strip())
            
            # Only block the 'local' user if they have failed 3 times
            if user == 'local' and failed_attempts[user] >= MAX_FAILED_ATTEMPTS:
                disable_user_ssh(user)
                failed_attempts[user] = 0  # Reset the counter after disabling the user
            elif user != 'local' and failed_attempts[user] >= MAX_FAILED_ATTEMPTS:
                print(f"Warning: {alias_user} has exceeded failed attempts, but no action will be taken.")
                failed_attempts[user] = 0  # Reset the counter to avoid constant logging for same user
    
    elif 'Accepted' in line:
        # Extract the username and IP from the "Accepted" line
        user_ip_match = re.search(r'Accepted \S+ for (\S+) from (\d+\.\d+\.\d+\.\d+)', line)
        
        if user_ip_match:
            user = user_ip_match.group(1)
            ip = user_ip_match.group(2)
            
            # Use alias if available, else use the original username
            alias_user = username_aliases.get(user, user)
            
            # Log the successful attempt
            log_entry = f"{time.ctime()} - Successful login for user {alias_user} from IP {ip}\n"
            log_entry_at_top(log_entry)
            print(log_entry.strip())
            
            # Reset failed attempts for the user on successful login
            if user in failed_attempts:
                failed_attempts[user] = 0

    time.sleep(0.5)  # Sleep briefly to avoid busy-waiting