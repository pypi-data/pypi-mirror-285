import pymel.core as pm
import json
from cwmaya.helpers import const as k
from cwmaya.windows import window_utils
from ciocore import data as coredata


def select_current_template(dialog):
    pm.select(dialog.node)


def duplicate_current_template(dialog):
    new_node = pm.duplicate(dialog.node, inputConnections=True)[0]
    dialog.load_template(new_node)


def show_spec(node):

    if not node:
        print("No node found")
        return

    out_attr = node.attr("output")
    pm.dgdirty(out_attr)
    payload = out_attr.get()

    payload = json.loads(payload)

    window_utils.show_in_vscode(payload)


def show_tokens(node):
    if not node:
        print("No node found")
        return

    out_attr = node.attr("tokens")
    pm.dgdirty(out_attr)
    payload = out_attr.get()
    data = json.loads(payload)
    window_utils.show_data_in_window(data, title="Tokens")


def export_spec(node):

    if not node:
        print("No node found")
        return

    out_attr = node.attr("output")
    pm.dgdirty(out_attr)
    payload = out_attr.get()

    filters = "JSON Files (*.json)"
    ws = pm.Workspace()
    datadir = ws.expandName(ws.fileRules.get("diskCache"))
    entries = pm.fileDialog2(
        caption="Save File As",
        okCaption="Export",
        fileFilter=filters,
        dialogStyle=2,
        fileMode=0,
        dir=datadir,
    )

    if not entries:
        print("No file selected")
        return

    with open(entries[0], "w", encoding="utf-8") as f:
        f.write(payload)
    print(f"Exported spec to {entries[0]}")
