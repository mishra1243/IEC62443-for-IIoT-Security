import os
import time

OTP_FILE = '/tmp/otp.txt'
SUDO_CONTROL_FILE = '/home/superadmin/sudo_control.txt'
VALID_OTP = 'secret123'  # Replace with your desired OTP
CHECK_INTERVAL = 5  # seconds
GRANT_DURATION = 15  # 2 minutes in seconds

def check_otp():
    if os.path.exists(OTP_FILE):
        with open(OTP_FILE, 'r') as f:
            otp = f.read().strip()
        
        if otp == VALID_OTP:
            grant_sudo_access()
            os.remove(OTP_FILE)
            return True
    return False

def grant_sudo_access():
    with open(SUDO_CONTROL_FILE, 'w') as f:
        f.write('1')
    print("Valid OTP entered. Sudo access granted for 15 seconds.")
    time.sleep(GRANT_DURATION)
    with open(SUDO_CONTROL_FILE, 'w') as f:
        f.write('0')
    print("Sudo access expired after 15 seconds.")

def main():
    while True:
        if check_otp():
            pass  # We've already handled the OTP in check_otp()
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()