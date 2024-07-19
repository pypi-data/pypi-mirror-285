import subprocess
import requests
import sys
import time


def check_for_updates(current_version):
    try:
        response = requests.get('https://pypi.org/pypi/support-toolbox/json')
        latest_version = response.json()['info']['version']
        if current_version < latest_version:
            print("One moment, you are on an outdated version of support-toolbox...")
            time.sleep(3)
            update_tool()
    except Exception as e:
        print(f"Failed to check for updates: {e}")
        return None


def update_tool():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'support-toolbox'])
        print("Update successful!")
    except Exception as e:
        print(f"Update failed: {e}")
