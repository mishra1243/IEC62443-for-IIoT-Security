import os
import time
import subprocess

SUDO_CONTROL_FILE = '/home/superadmin/sudo_control.txt'
ADMIN_USERNAME = 'z004ymtp'

def read_sudo_control():
    if os.path.exists(SUDO_CONTROL_FILE):
        with open(SUDO_CONTROL_FILE, 'r') as f:
            return f.read().strip()
    return '0'

def set_sudo_access(allow):
    if allow:
        subprocess.run(['sudo', 'usermod', '-aG', 'sudo', ADMIN_USERNAME])
        print(f"Sudo access granted to {ADMIN_USERNAME}")
    else:
        subprocess.run(['sudo', 'deluser', ADMIN_USERNAME, 'sudo'])
        print(f"Sudo access revoked from {ADMIN_USERNAME}")

def main():
    while True:
        sudo_status = read_sudo_control()
        if sudo_status == '1':
            set_sudo_access(True)
        else:
            set_sudo_access(False)
        time.sleep(10)  # Check every 10 seconds

if __name__ == '__main__':
    main()