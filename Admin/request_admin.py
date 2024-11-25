import requests
import time
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(filename='/home/z004ymtp/Logs/sudo_requests.txt', level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def check_sudo_access():
    with open('/home/superadmin/sudo_control.txt', 'r') as f:
        return f.read().strip() == '1'

def send_request():
    try:
        logging.info("Sending sudo access request")
        response = requests.post('http://localhost:5000/request_access', json={'user': 'z004ymtp'})
        if response.status_code == 200:
            print("Request sent successfully. Waiting for superadmin's response...")
            logging.info("Request sent successfully. Waiting for response.")
            
            # Wait for response
            for _ in range(60):  # Wait for up to 1 minute
                time.sleep(1)
                if check_sudo_access():
                    print("Request approved. You now have sudo access for 5 minutes.")
                    logging.info("Request approved. Sudo access granted for 5 minutes.")
                    return
            
            print("Request timed out or was declined.")
            logging.info("Request timed out or was declined.")
        else:
            print("Failed to send request. Server responded with:", response.status_code)
            logging.error(f"Failed to send request. Server responded with: {response.status_code}")
    except requests.RequestException as e:
        print("Failed to send request:", str(e))
        logging.error(f"Failed to send request: {str(e)}")

if __name__ == "__main__":
    if os.geteuid() == 0:
        print("You already have sudo privileges.")
        logging.info("Script run with sudo privileges.")
    elif check_sudo_access():
        print("You already have sudo access.")
        logging.info("User already has sudo access.")
    else:
        send_request()