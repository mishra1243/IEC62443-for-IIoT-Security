import gpiod
import psutil
import hashlib
import paho.mqtt.client as mqtt
import time
from datetime import datetime
import os
import threading

# Global variables to track last known status
last_admin_status = None
last_local_status = None
last_signal_1_status = None
last_signal_2_status = None

# MQTT settings
MQTT_BROKER = "localhost"  # Change this to your MQTT broker address
MQTT_PORT = 1883           # Default MQTT port
MQTT_TOPICS = {
    "signal1": "control/signal1",
    "signal2": "control/signal2",
    "signal3": "control/signal3",
    "signal4": "control/signal4",
    "signal5": "control/signal5",
    "text_message": "control/text_message"
}

# MQTT Client setup
client = mqtt.Client()

# Connect to the MQTT broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Function to simulate control signal logic
def determine_signal_1():
    button_pin = 4
    
    try:
        # Set up GPIO button line
        chip = gpiod.Chip('gpiochip4')
        button_line = chip.get_line(button_pin)
        button_line.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
        
        # Get the button state
        button_state = button_line.get_value()
        
        # Release the button line
        button_line.release()
        
        # Return True if button state is 0 (pressed), False if 1 (not pressed)
        return button_state == 0
        
    except Exception as e:
        print(f"Error reading button state: {str(e)}")
        return False


def determine_signal_2():
    config_file = "/home/z004ymtp/Secret/config.txt"
    
    try:
        with open(config_file, "r") as f:
            config = f.readlines()
        
        file_path = config[0].strip().split('=')[1]
        predetermined_sha256 = config[1].strip().split('=')[1]
        
        with open(file_path, "rb") as f:
            sha256 = hashlib.sha256()
            while True:
                data = f.read(65536)  # Read file in chunks of 64KB
                if not data:
                    break
                sha256.update(data)
        
        calculated_sha256 = sha256.hexdigest()
        
        return calculated_sha256 == predetermined_sha256
    
    except FileNotFoundError:
        print(f"Config file '{config_file}' not found or does not exist.")
        return False
    except Exception as e:
        print(f"Error occurred while calculating SHA256: {str(e)}")
        return False

def determine_signal_3():
    admin_user = "z004ymtp"

    try:
        users = psutil.users()
        for user in users:
            if user.name == admin_user and user.terminal and user.terminal.startswith('pts'):
                return True
    except Exception as e:
        print(f"Error checking SSH sessions: {str(e)}")

    return False

def determine_signal_4():
    local_user = "local"

    try:
        users = psutil.users()
        for user in users:
            if user.name == local_user and user.terminal and user.terminal.startswith('pts'):
                return True
    except Exception as e:
        print(f"Error checking SSH sessions: {str(e)}")

    return False

def determine_signal_5():
    file_path='/home/z004ymtp/Logs/auth_log.txt'
    """
    Checks the first line of a file to determine if a user has been temporarily disabled.
    
    :param file_path: Path to the file to be read.
    :return: False if the first line matches the specified message, True otherwise.
    """
    try:
        with open(file_path, 'r') as file:
            first_line = file.readline().strip()
            if "User Local has been temporarily disabled due to exceeding maximum failed login attempts." in first_line:
                return False
            else:
                return True
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def update_log(log_message):
    config_file = "/home/z004ymtp/Secret/config.txt"
    log_file_path = None
    
    try:
        with open(config_file, "r") as f:
            for line in f:
                if line.strip().startswith("log_file_path"):
                    log_file_path = line.strip().split('=')[1]
                    break
            
            if not log_file_path:
                print("Log file path not found in config.txt")
                return False
    except FileNotFoundError:
        print(f"Config file '{config_file}' not found or does not exist.")
        return False
    except Exception as e:
        print(f"Error reading config file: {str(e)}")
        return False
    
    try:
        if os.path.exists(log_file_path):
            with open(log_file_path, "r") as f:
                existing_logs = f.readlines()
        else:
            existing_logs = []
        
        with open(log_file_path, "w") as f:
            f.write(f"{log_message}\n")
            for log in existing_logs:
                f.write(log)
        
        return True
    except Exception as e:
        print(f"Error updating log file: {str(e)}")
        return False

def determine_text_message():
    config_file = "/home/z004ymtp/Secret/config.txt"
    log_file_path = None
    
    try:
        with open(config_file, "r") as f:
            for line in f:
                if line.strip().startswith("log_file_path"):
                    log_file_path = line.strip().split('=')[1]
                    break
            
            if not log_file_path:
                print("Log file path not found in config.txt")
                return "System operational"
    except FileNotFoundError:
        print(f"Config file '{config_file}' not found or does not exist.")
        return "System operational"
    except Exception as e:
        print(f"Error reading config file: {str(e)}")
        return "System operational"
    
    try:
        with open(log_file_path, "r") as f:
            first_line = f.readline().strip()
            return first_line if first_line else "System operational"
    except FileNotFoundError:
        print(f"Log file '{log_file_path}' not found or does not exist.")
        return "System operational"
    except Exception as e:
        print(f"Error reading log file: {str(e)}")
        return "System operational"

def monitor_user_events():
    global last_admin_status, last_local_status, last_signal_1_status, last_signal_2_status
    
    try:
        while True:
            admin_status = determine_signal_3()
            if admin_status != last_admin_status:
                if admin_status:
                    log_message = f"Admin logged in at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                else:
                    log_message = f"Admin logged out at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                if update_log(log_message):
                    print(f"Updated log: {log_message}")
                    last_admin_status = admin_status
                else:
                    print("Failed to update log file.")
            
            local_status = determine_signal_4()
            if local_status != last_local_status:
                if local_status:
                    log_message = f"Local user logged in at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                else:
                    log_message = f"Local user logged out at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                if update_log(log_message):
                    print(f"Updated log: {log_message}")
                    last_local_status = local_status
                else:
                    print("Failed to update log file.")
            
            signal_1_status = determine_signal_1()
            if signal_1_status != last_signal_1_status:
                if signal_1_status:
                    log_message = f"Case closed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                else:
                    log_message = f"Case opened at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                if update_log(log_message):
                    print(f"Updated log: {log_message}")
                    last_signal_1_status = signal_1_status
                else:
                    print("Failed to update log file.")
            
            signal_2_status = determine_signal_2()
            if signal_2_status != last_signal_2_status:
                if signal_2_status:
                    log_message = f"Firmware OK at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                else:
                    log_message = f"Someone changed the firmware at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                if update_log(log_message):
                    print(f"Updated log: {log_message}")
                    last_signal_2_status = signal_2_status
                else:
                    print("Failed to update log file.")
            
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("Stopping log monitoring...")

def send_control_signals_and_text():
    try:
        while True:
            signal_1 = determine_signal_1()
            signal_2 = determine_signal_2()
            signal_3 = determine_signal_3()
            signal_4 = determine_signal_4()
            signal_5 = determine_signal_5()
            text_message = determine_text_message()

            client.publish(MQTT_TOPICS["signal1"], payload=signal_1, qos=0, retain=False)
            client.publish(MQTT_TOPICS["signal2"], payload=signal_2, qos=0, retain=False)
            client.publish(MQTT_TOPICS["signal3"], payload=last_admin_status, qos=0, retain=False)
            client.publish(MQTT_TOPICS["signal4"], payload=last_local_status, qos=0, retain=False)
            client.publish(MQTT_TOPICS["signal5"], payload=signal_5, qos=0, retain=False)
            client.publish(MQTT_TOPICS["text_message"], payload=text_message, qos=0, retain=False)

            print(f"Published signals: {signal_1}, {signal_2}, {last_admin_status}, {last_local_status}, {signal_5}")
            print(f"Published text message: {text_message}")

            time.sleep(2)
    except KeyboardInterrupt:
        print("Stopping MQTT server control signal and text message script...")
        client.disconnect()

if __name__ == "__main__":
    user_event_thread = threading.Thread(target=monitor_user_events)
    user_event_thread.start()
    
    send_control_signals_and_text()