import os
import time
# File paths
file_path = "/tmp/otp.txt"
control_file = "/home/superadmin/sudo_control.txt"

# Get user input
user_text = input("Please enter the text to write to /tmp/otp.txt: ")

# Write the input to /tmp/otp.txt and set permissions to be writable by others
with open(file_path, "w") as file:
    file.write(user_text)

# Set permissions to allow read and write access for everyone
os.chmod(file_path, 0o644)  # rw-rw-rw-
time.sleep(5)
# Check the contents of /home/superadmin/sudo_control.txt
try:
    with open(control_file, "r") as control:
        control_value = control.read().strip()
        if control_value == "1":
            print("OTP accepted")
        else:
            print("Correct OTP not provided")
except FileNotFoundError:
    print(f"Control file {control_file} not found.")
except PermissionError:
    print(f"Permission denied when accessing {control_file}.")