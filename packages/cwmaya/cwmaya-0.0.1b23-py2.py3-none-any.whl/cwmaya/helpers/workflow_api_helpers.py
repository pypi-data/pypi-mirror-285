import pymel.core as pm
import os
import json

import requests

from cwmaya.helpers import const as k
from cwmaya.windows import window_utils
from cwmaya.windows import jobs_index
from ciocore import data as coredata
from cwmaya.helpers import desktop_app_helpers 

from contextlib import contextmanager


@contextmanager
def save_scene():
    """
    A context manager to save the current scene before executing the block of code.

    Yields:
        None: Yields control back to the context block after saving the scene.

    Usage Example:
    ```
    with save_scene():
        # Perform actions that require the scene to be saved
    ```
    """
    try:
        if pm.isModified():
            filters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
            entries = pm.fileDialog2(
                caption="Save File As",
                okCaption="Save As",
                fileFilter=filters,
                dialogStyle=2,
                fileMode=0,
                dir=os.path.dirname(pm.sceneName()),
            )
            if entries:
                filepath = entries[0]
                pm.saveAs(filepath)
        yield
    except Exception as err:
        pm.displayError(str(err))
    finally:
        pass


##### WORKFLOW API DISPLAY FUNCTIONS #####
def validate_job(node):
    try:
        response = request_validate_job(node)
        data = {"status_code": response.status_code, "text": response.text}
    except Exception as err:
        data = {"error": str(err)}
    window_utils.show_data_in_window(data, title="Workflow API | Validate job")


def health_check():
    try:
        response = request_health_check()
        data = {"status_code": response.status_code, "text": response.text}
    except Exception as err:
        data = {"error": str(err)}
    window_utils.show_data_in_window(data, title="Workflow API | Health check")


def list_jobs():
    try:
        response = request_list_jobs()

        # Check if the status code is an error code (4xx or 5xx)
        if response.status_code > 201:
            # You can raise a built-in HTTPError or define your own exception
            raise Exception(f"Error response {response.status_code}: {response.text}")

        data = json.loads(response.text)
    except Exception as err:
        data = {"error": str(err)}

    win = jobs_index.JobsIndex()
    win.hydrate(data)


def show_job(job):
    response = request_get_job(job["id"])
    try:
        if response.status_code > 201:
            raise Exception(f"Error response {response.status_code}: {response.text}")
        data = json.loads(response.text)
    except Exception as err:
        data = {"error": str(err)}

    window_utils.show_data_in_window(data, title="Workflow API | Show Job")


def show_nodes(job):
    response = request_get_nodes(job["id"])
    try:
        if response.status_code > 201:
            raise Exception(f"Error response {response.status_code}: {response.text}")
        data = json.loads(response.text)
    except Exception as err:
        data = {"error": str(err)}

    window_utils.show_data_in_window(data, title="Workflow API | Show Nodes")


def show_nodes_in_vscode(job):
    response = request_get_nodes(job["id"])
    try:
        if response.status_code > 201:
            raise Exception(f"Error response {response.status_code}: {response.text}")
        data = json.loads(response.text)
    except Exception as err:
        data = {"error": str(err)}

    window_utils.show_in_vscode(data)


def show_spec_in_vscode(job):
    response = request_get_spec(job["id"])
    try:
        if response.status_code > 201:
            raise Exception(f"Error response {response.status_code}: {response.text}")
        data = json.loads(response.text)
    except Exception as err:
        data = {"error": str(err)}

    window_utils.show_in_vscode(data)
    
# def show_wf_spec_in_vscode()

def submit(node):
    """
    Submit the current job in the current template to the workflow api.
    
    Once submitted, get the workflow id and send it to the monitor in the desktop app.
    """
    if not node:
        print("No node found")
        return
    # try to force the output plug to update because I noticed some anomalies - old values in the submission 
    out_attr = node.attr("output")
    pm.dgdirty(out_attr)
    
    with save_scene():
 
        out_attr = node.attr("output")
        pm.dgdirty(out_attr) 
        payload = out_attr.get()
        account_id = coredata.data()["account"]["account_id"]
        token = coredata.data()["account"]["token"]
        url_base = k.WORKFLOW_URLS["ACCOUNTS"]
        url = f"{url_base}/{account_id}/workflows"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        print("Response:", response.status_code)
        
        if response.status_code <= 201:
            print("Successfully submitted job")
        else:
            pm.error("Error submitting job:", response.text)
            return
        
        response_data = json.loads(response.text)
        
        workflow_id = response_data["id"]
        with desktop_app_helpers.desktop_app():
            url = k.DESKTOP_URLS["MONITOR"]
            token = coredata.data()["account"]["token"]
            data = json.dumps({"token": token, "workflow_id": workflow_id})
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(url, data=data, headers=headers, timeout=10)
            if response.status_code == 200:
                print("Successfully sent id to monitor")
            else:
                pm.error("Error sending id to monitor:", response.text)
 
def request_submit(node):
    headers = {"Content-Type": "application/json"}
    out_attr = node.attr("output")
    pm.dgdirty(out_attr)
    payload = out_attr.get()

    account_id = coredata.data()["account"]["account_id"]
    token = coredata.data()["account"]["token"]
    url = k.WORKFLOW_URLS["ACCOUNTS"]
    url = f"{url}/{account_id}/workflows"

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    return requests.post(url, data=payload, headers=headers, timeout=5)


def export_submission(node):
    if not node:
        print("No node found")
        return

    CONDUCTOR_URL = os.environ.get(
        "CONDUCTOR_URL", "https://dashboard.conductortech.com"
    )

    headers = {"Content-Type": "application/json"}
    out_attr = node.attr("output")
    pm.dgdirty(out_attr)
    payload = out_attr.get()
    account_id = coredata.data()["account"]["account_id"]
    token = coredata.data()["account"]["token"]
    url = k.WORKFLOW_URLS["ACCOUNTS"]
    url = f"{url}/{account_id}/workflows"

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    filters = "Python Files (*.py)"
    ws = pm.Workspace()
    datadir = ws.expandName(ws.fileRules.get("scripts"))
    entries = pm.fileDialog2(
        caption="Save Script As",
        okCaption="Export",
        fileFilter=filters,
        dialogStyle=2,
        fileMode=0,
        dir=datadir,
    )

    if not entries:
        print("No file selected")
        return

    scriptfile = entries[0]

    with open(scriptfile, "w") as f:
        f.write(f"import os\n")
        f.write(f"os.environ['CONDUCTOR_URL'] = '{CONDUCTOR_URL}'\n\n")
        f.write(f"import requests\n\n")
        f.write(f"headers = {headers}\n\n")
        f.write(f"payload = '{payload}'\n\n")
        f.write(f"account_id = '{account_id}'\n\n")
        f.write(f"token = '{token}'\n\n")
        f.write(f"url = '{url}'\n\n")
        f.write(
            f"response = requests.post(url, data=payload, headers=headers, timeout=5)\n"
        )
        f.write(f"print(response.text)\n")

    pm.displayInfo(f"Script saved to {scriptfile}")

    # open the script in vscode if available
    try:
        window_utils.show_file_in_vscode(scriptfile)
    except Exception as err:
        pm.displayError(str(err))



##### WORKFLOW API REQUESTS #####
def request_health_check():
    url = k.WORKFLOW_URLS["HEALTHZ"]
    headers = {"Content-Type": "application/json"}
    return requests.get(url, headers=headers, timeout=5)


def request_list_jobs():
    account_id = coredata.data()["account"]["account_id"]
    token = coredata.data()["account"]["token"]
    url = k.WORKFLOW_URLS["ACCOUNTS"]
    url = f"{url}/{account_id}/workflows"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    return requests.get(url, headers=headers, timeout=5)

def get_job_url(id):
    account_id = coredata.data()["account"]["account_id"]
    url = k.WORKFLOW_URLS["ACCOUNTS"]
    url = f"{url}/{account_id}/workflows/{id}"
    return url

def request_get_job(id):
    url =get_job_url(id)
    print("URL:", url)
    token = coredata.data()["account"]["token"]
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    return requests.get(url, headers=headers, timeout=5)

def get_nodes_url(id):
    account_id = coredata.data()["account"]["account_id"]
    url = k.WORKFLOW_URLS["ACCOUNTS"]
    url = f"{url}/{account_id}/workflows/{id}/nodes"
    return url
    
def request_get_nodes(id):
    url = get_nodes_url(id)
    print("URL:", url)
    token = coredata.data()["account"]["token"]
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    return requests.get(url, headers=headers, timeout=5)


def get_spec_url(id):
    account_id = coredata.data()["account"]["account_id"]
    url = k.WORKFLOW_URLS["ACCOUNTS"]
    url = f"{url}/{account_id}/workflows/{id}/spec"
    return url
    
def request_get_spec(id):
    url = get_spec_url(id)
    print("URL:", url)
    token = coredata.data()["account"]["token"]
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    return requests.get(url, headers=headers, timeout=5)


def request_validate_job(node):
    headers = {"Content-Type": "application/json"}
    out_attr = node.attr("output")

    pm.dgdirty(out_attr)
    payload = out_attr.get()
    token = coredata.data()["account"]["token"]
    url = k.WORKFLOW_URLS["VALIDATE"]
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    return requests.post(url, data=payload, headers=headers, timeout=5)
