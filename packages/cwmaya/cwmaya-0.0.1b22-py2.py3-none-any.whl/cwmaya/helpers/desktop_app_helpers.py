import pymel.core as pm
from cwmaya.windows import window_utils

import requests
import json
from cwmaya.helpers import const as k
from ciocore import data as coredata
from contextlib import contextmanager
import subprocess
import platform
import psutil
import time

from cwmaya.helpers.conductor_helpers import (
    get_packages_model,
    get_projects_model,
    get_instance_types_model,
)

APP_NAME = "Conductor"


def get_app_locations():
    system = platform.system()
    if system == "Darwin":  # macOS
        return [
            f"/Applications/{APP_NAME}.app",
            f"/Volumes/xhf/dev/cio/cioapp/src-tauri/target/release/bundle/macos/{APP_NAME}.app",
        ]
    elif system == "Windows":
        return [
            f"C:\\Program Files\\{APP_NAME}",
            f"C:\\Users\\{platform.node()}\\AppData\\Local\\{APP_NAME}",
        ]
    elif system == "Linux":
        return [
            f"/usr/local/bin/{APP_NAME}",
            f"/opt/{APP_NAME}",
            f"/home/{platform.node()}/.local/share/{APP_NAME}",
        ]
    else:
        raise NotImplementedError(f"Unsupported OS: {system}")


def is_app_running():
    """Check if a given application is currently running and return its PID."""
    for proc in psutil.process_iter(["name", "pid"]):
        if proc.info["name"] == APP_NAME:
            return True, proc.info["pid"]
    return False, None

@contextmanager
def desktop_app():
    """
    A context manager to check the health of the desktop application and open it if necessary.

    Yields:
        tuple: (location, pid) if the app is successfully opened and healthy.

    Usage Example:
    ```
    with desktop_app() as (location, pid):
        # Perform actions when the desktop app is healthy
    ```

    If the health check fails, a window is displayed with the response or error message using `window_utils.show_data_in_window`.
    """
    errors = None
    app_location = None
    app_pid = None

    try:
        # Check if the app is already running
        is_running, pid = is_app_running()
        if is_running:
            print(f"{APP_NAME} is already running with PID {pid}.")
            yield (None, pid)
            return
        
        healthy = is_app_healthy()
        if not healthy:
            print(f"{APP_NAME} is not healthy. Attempting to open {APP_NAME}...")

            for location in get_app_locations():
                print(f"Trying to open {location}...")
                try:
                    process = subprocess.Popen(
                        ["open", location],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    stdout, stderr = process.communicate()

                    if process.returncode == 0:
                        print(f"Successfully opened {location}")
                        app_location = location
                        app_pid = process.pid
                        time.sleep(2)
                        break
                    else:
                        print(f"Failed to open {location}: {stderr.decode().strip()}")
                except Exception as e:
                    print(f"Exception occurred while trying to open {location}: {e}")

            # Recheck health after attempting to open the app
            healthy = is_app_healthy()

        if healthy:
            yield (app_location, app_pid)  # Yield location and pid here
        else:
            yield (None, None)  # Yield None values if there's an error
    except Exception as err:
        errors = {"error": str(err)}
        yield (None, None)  # Yield None values if there's an exception
    finally:
        if errors:
            window_utils.show_data_in_window(errors, title="Desktop app status")


############################################### HEALTH
def health_check():
    try:
        response = request_health_check()
        data = {"status_code": response.status_code, "text": response.text}
    except Exception as err:
        data = {"error": str(err)}
    window_utils.show_data_in_window(data, title="Desktop app health check")


def request_health_check():
    url = k.DESKTOP_URLS["HEALTHZ"]
    headers = {"Content-Type": "application/json"}
    return requests.get(url, headers=headers, timeout=5)


def is_app_healthy():
    """Check if a given application is currently running"""
    try:
        response = request_health_check()
        if response.ok:
            return True
    except Exception as err:
        pass
    return False


##############################################


def navigate(route):
    response = request_navigate_route(route)
    if response.status_code == 200:
        print(f"Successfully navigated to {route}")
    else:
        pm.error(f"Error navigating to {route}: {response.text}")

def send_to_composer(node):
    if not node:
        print("No node found")
        return
    with desktop_app():
        url = k.DESKTOP_URLS["COMPOSER"]
        headers = {"Content-Type": "application/json"}
        out_attr = node.attr("output")
        pm.dgdirty(out_attr)
        payload = out_attr.get()
        response = requests.post(url, data=payload, headers=headers, timeout=5)
        if response.status_code == 200:
            print("Successfully sent payload to composer")
        else:
            pm.error("Error sending payload to composer:", response.text)


def send_to_monitor(workflow_id):
    with desktop_app():
        url = k.DESKTOP_URLS["MONITOR"]
        headers = {"Content-Type": "application/json"}
        token = coredata.data()["account"]["token"]
        data = json.dumps({"token": token, "workflow_id": workflow_id})

        response = requests.post(url, data=data, headers=headers, timeout=5)
        if response.status_code == 200:
            print("Successfully sent id to monitor")
        else:
            pm.error("Error sending id to monitor:", response.text)
 
def authenticate():
    with desktop_app():
        token = coredata.data()["account"]["token"]
        url = k.DESKTOP_URLS["AUTH"]
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            url, data=json.dumps({"token": token}), headers=headers, timeout=5
        )
        if response.status_code == 200:
            print("Successfully authenticated with desktop app")
        else:
            pm.error("Error authenticating with desktop app:", response.text)
        return response


##### DESKTOP APP REQUESTS #####


def request_navigate_route(route):
    if not route.startswith("/"):
        route = f"/{route}"

    url = k.DESKTOP_URLS["NAVIGATE"]
    data = json.dumps({"to": route})
    headers = {"Content-Type": "application/json"}
    return requests.post(url, data=data, headers=headers, timeout=5)


def send_coredata():
    with desktop_app():
        url = k.DESKTOP_URLS["COREDATA"]
        headers = {"Content-Type": "application/json"}

        data = {
            "token": coredata.data()["account"]["token"],
            "projects": get_projects_model(),
            "packages": get_packages_model(),
            "instance_types": get_instance_types_model(),
        }
        payload = json.dumps(data)
        response = requests.post(url, data=payload, headers=headers, timeout=5)
        if response.status_code == 200:
            print("Successfully sent payload to desktop app")
        else:
            pm.error("Error sending payload to desktop app:", response.text)
        return response


def open_app():
    with desktop_app() as (location, pid):
        pass