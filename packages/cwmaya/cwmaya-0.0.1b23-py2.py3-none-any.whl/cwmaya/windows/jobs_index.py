import pymel.core.uitypes as gui
import pymel.core as pm
import json
from cwmaya.helpers import const as k
from cwmaya.helpers import workflow_api_helpers, desktop_app_helpers

from datetime import datetime


class JobsIndex(gui.Window):

    def __init__(self):
        super(JobsIndex, self).__init__()

        others = pm.lsUI(windows=True)
        for win in others:
            title = pm.window(win, q=True, title=True)
            if title == k.JOBS_INDEX_WINDOW_TITLE:
                pm.deleteUI(win)

        # self.data = data
        self.setTitle(k.JOBS_INDEX_WINDOW_TITLE)
        self.setIconName(k.JOBS_INDEX_WINDOW_TITLE)
        self.setWidthHeight(k.WINDOW_DIMENSIONS)

        self.form = pm.formLayout(nd=100)
        pm.setParent(self.form)
        self.scroll = pm.scrollLayout(childResizable=True)
        pm.setParent(self.scroll)
        self.column = pm.columnLayout(adj=True)

        pm.setParent(self.form)
        self.refresh_but = pm.button(
            label="Refresh", command=pm.Callback(self.on_refresh)
        )
        self.cancel_but = pm.button(label="Cancel", command=pm.Callback(self.on_cancel))
        self.layoutForm()

        self.show()
        self.setResizeToFitChildren()

    def hydrate(self, data):
        """
            #   "id": 4233184804521581, -
            #   "created_at": "2024-06-08T19:14:40Z", -
            #   "updated_at": "2024-06-08T19:14:40Z",
            #   "account_id": "5669544198668288",
            #   "short_id": "00000", -
            #   "name": "Job_1", -
            #   "user": "jmann", -
            #   "project": "default", -
            #   "progress": 33, -
            #   "status": "incomplete", -
            #   "version": "0.0.1",
            #   "priority": 5,
            #   "edges": {}
            # 
        """
        pm.setParent(self.column)
        widgets = pm.columnLayout(self.column, q=True, ca=True)
        if widgets:
            pm.deleteUI(widgets)

        if "error" in data:
            pm.text(label=data["error"])
            return

        for job in data:
            self.create_job_widget(job, self.column)



    def create_job_widget(self, job, parent):
        pm.setParent(parent)
        frame = pm.frameLayout(
            labelVisible=False, borderVisible=True, collapsable=False, collapse=False
        )
        form = pm.formLayout(nd=100)
        created = datetime.strptime(job["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        created = created.strftime("%b %d %Y %H:%M:%S")

        label_widgets = []
        label_widgets.append(self.create_label_field("Short ID", job["short_id"], form))
        label_widgets.append(self.create_label_field("Name", job["name"], form))
        label_widgets.append(self.create_label_field("Unique ID", job["id"], form))
        label_widgets.append(
            self.create_label_field("Account", job["account_id"], form)
        )
        label_widgets.append(self.create_label_field("Project", job["project"], form))
        label_widgets.append(self.create_label_field("User", job["user"], form))
        label_widgets.append(self.create_label_field("Status", job["status"], form))
        label_widgets.append(self.create_label_field("Progress", job["progress"], form))
        label_widgets.append(self.create_label_field("Created At", created, form))
        label_widgets.append(self.create_label_field("Version", job["version"], form))

        pm.setParent(form)
        show_job_but = pm.button(
            label="Show Job",
            ann=workflow_api_helpers.get_job_url(job["id"]),
            command=pm.Callback(
                workflow_api_helpers.show_job,
                job
            )
        )
        show_spec_but = pm.button(
            label="Show Spec in VSCode",
            ann=workflow_api_helpers.get_spec_url(job["id"]),
            command=pm.Callback(workflow_api_helpers.show_spec_in_vscode, job),
        )
        show_nodes_in_vscode_but = pm.button(
            label="Show Nodes in VSCode",
            ann=workflow_api_helpers.get_nodes_url(job["id"]),
            command=pm.Callback(workflow_api_helpers.show_nodes_in_vscode, job),
        )
        monitor_but = pm.button(
            label="Monitor Job",
            command=pm.Callback(desktop_app_helpers.send_to_monitor, job["id"]),
        )

        form.attachForm(show_job_but, "top", 2)
        form.attachPosition(show_job_but, "left", 2, 80)
        form.attachForm(show_job_but, "right", 2)
        form.attachPosition(show_job_but, "bottom", 2, 25)

        form.attachControl(show_nodes_in_vscode_but, "top", 2, show_job_but)
        form.attachPosition(show_nodes_in_vscode_but, "left", 2, 80)
        form.attachForm(show_nodes_in_vscode_but, "right", 2)
        form.attachPosition(show_nodes_in_vscode_but, "bottom", 2, 50)
        
        form.attachControl(show_spec_but, "top", 2, show_nodes_in_vscode_but)
        form.attachPosition(show_spec_but, "left", 2, 80)
        form.attachForm(show_spec_but, "right", 2)
        form.attachPosition(show_spec_but, "bottom", 2, 75)

        form.attachControl(monitor_but, "top", 2, show_spec_but)
        form.attachPosition(monitor_but, "left", 2, 80)
        form.attachForm(monitor_but, "right", 2)
        form.attachForm(monitor_but, "bottom", 2)

        side = "left"
        for i, label in enumerate(label_widgets):
            row_num = i // 2
            last_row = row_num == len(label_widgets) // 2
            side = "left" if i % 2 == 0 else "right"
            top_row = i < 2

            # top
            if top_row:
                form.attachForm(label, "top", 2)
            else:
                form.attachControl(label, "top", 2, label_widgets[i - 2])

            # bottom
            if last_row:
                form.attachForm(label, "bottom", 2)
            else:
                form.attachNone(label, "bottom")

            # right
            if side == "left":
                form.attachPosition(label, "right", 2, 40)
            else:
                form.attachForm(label, "right", 2)

            # left
            if side == "right":
                form.attachControl(label, "left", 2, label_widgets[i - 1])
            else:
                form.attachForm(label, "left", 2)
        return frame

    def create_label_field(self, label, value, parent):
        pm.setParent(parent)
        row = pm.rowLayout(nc=4, cw4=(10, 65, 10, 200), adjustableColumn=4)
        pm.text(label=" ", height=20, width=10, align="left")
        pm.text(label=f"{label}:", height=20, width=65, align="left")
        pm.text(label=" ", height=20, width=10, align="left")
        pm.text(
            label=f" {value}",
            height=20,
            align="left",
            enableBackground=True,
            backgroundColor=(0.2, 0.2, 0.2),
        )
        return row

    def layoutForm(self):

        self.form.attachForm(self.scroll, "top", 2)
        self.form.attachForm(self.scroll, "left", 2)
        self.form.attachForm(self.scroll, "right", 2)
        self.form.attachControl(self.scroll, "bottom", 2, self.refresh_but)

        self.form.attachNone(self.refresh_but, "top")
        self.form.attachPosition(self.refresh_but, "left", 2, 50)
        self.form.attachForm(self.refresh_but, "right", 2)
        self.form.attachForm(self.refresh_but, "bottom", 2)

        self.form.attachNone(self.cancel_but, "top")
        self.form.attachControl(self.cancel_but, "right", 2, self.refresh_but)
        self.form.attachForm(self.cancel_but, "left", 2)
        self.form.attachForm(self.cancel_but, "bottom", 2)

    def on_refresh(self):
        response = workflow_api_helpers.request_list_jobs()
        try:
            if response.status_code > 201:
                raise Exception(
                    f"Error response {response.status_code}: {response.text}"
                )

            data = json.loads(response.text)
        except Exception as err:
            data = {"error": str(err)}
        self.hydrate(data)

    def on_cancel(self):
        print("on_cancel")
