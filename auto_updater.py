import os
import sys
import requests
import subprocess
import time

# Constants
CURRENT_VERSION = '1.0.0'
VERSION_URL = 'https://raw.githubusercontent.com/your-username/your-repo/main/version.txt'
UPDATE_URL = 'https://raw.githubusercontent.com/your-username/your-repo/main/your_app.py'
APP_FILE = 'your_app.py'

def get_latest_version():
    response = requests.get(VERSION_URL)
    response.raise_for_status()
    return response.text.strip()

def download_update():
    response = requests.get(UPDATE_URL)
    response.raise_for_status()
    with open(APP_FILE, 'wb') as file:
        file.write(response.content)

def update_and_restart():
    download_update()
    print("Update downloaded. Restarting...")
    # On Windows, use 'python' instead of 'python3' if needed
    os.execv(sys.executable, ['python3'] + sys.argv)

def main():
    print(f"Current version: {CURRENT_VERSION}")
    try:
        latest_version = get_latest_version()
        print(f"Latest version: {latest_version}")

        if latest_version != CURRENT_VERSION:
            print("New version available. Updating...")
            update_and_restart()
        else:
            print("You are already using the latest version.")
    except requests.RequestException as e:
        print(f"Failed to check for updates: {e}")

    # Your main application code here
    print("Running application...")
    while True:
        time.sleep(1)  # Simulate work

if __name__ == '__main__':
    main()
