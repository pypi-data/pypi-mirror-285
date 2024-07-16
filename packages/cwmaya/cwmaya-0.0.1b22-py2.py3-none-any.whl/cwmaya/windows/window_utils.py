import pymel.core as pm
import json
import subprocess
import cwmaya.helpers.const as k


def layout_form(form, text, main_layout, *buttons):
    form.attachForm(text, "left", k.FORM_SPACING_X)
    form.attachForm(text, "right", k.FORM_SPACING_X)
    form.attachForm(text, "top", k.FORM_SPACING_Y)
    form.attachNone(text, "bottom")

    form.attachForm(main_layout, "left", k.FORM_SPACING_X)
    form.attachForm(main_layout, "right", k.FORM_SPACING_X)
    form.attachControl(main_layout, "top", k.FORM_SPACING_Y, text)
    form.attachControl(main_layout, "bottom", k.FORM_SPACING_Y, buttons[0])

    form.attachForm(buttons[0], "left", k.FORM_SPACING_X)
    form.attachNone(buttons[0], "top")
    form.attachForm(buttons[0], "bottom", k.FORM_SPACING_Y)

    if len(buttons) == 1:
        form.attachForm(buttons[0], "right", k.FORM_SPACING_X)
    else:  # 2
        form.attachPosition(buttons[0], "right", k.FORM_SPACING_X, 50)

        form.attachPosition(buttons[1], "left", k.FORM_SPACING_X, 50)
        form.attachForm(buttons[1], "right", k.FORM_SPACING_X)
        form.attachNone(buttons[1], "top")
        form.attachForm(buttons[1], "bottom", k.FORM_SPACING_Y)


def ensure_unique_window(title):
    """
    Ensure that only one window is open at a time.
    """
    others = pm.lsUI(windows=True)
    for win in others:
        existing_title = pm.window(win, q=True, title=True)
        if title == existing_title:
            pm.deleteUI(win)


def show_as_json(data, **kw):
    title = kw.get("title", "Json Window")
    indent = kw.get("indent", 2)
    sort_keys = kw.get("sort_keys", True)
    result_json = json.dumps(data, indent=indent, sort_keys=sort_keys)
    pm.window(width=600, height=800, title=title)
    pm.frameLayout(cll=False, lv=False)
    pm.scrollField(text=result_json, editable=False, wordWrap=False)
    pm.showWindow()


def show_data_in_window(data, **kw):
    title = kw.get("title", "Window")
    ensure_unique_window(title)
    result_json = json.dumps(data, indent=2)
    pm.window(width=600, height=800, title=title)
    pm.frameLayout(cll=False, lv=False)
    pm.scrollField(text=result_json, editable=False, wordWrap=False)
    pm.showWindow()


def show_text_in_window(text, **kw):
    title = kw.get("title", "Window")
    ensure_unique_window(title)
    pm.window(width=600, height=800, title=title)
    pm.frameLayout(cll=False, lv=False)
    pm.scrollField(text=text, editable=False, wordWrap=False)
    pm.showWindow()


def show_in_vscode(data, **kw):
    json_str = json.dumps(data, indent=3)
    process = subprocess.Popen(["/usr/local/bin/code", "-"], stdin=subprocess.PIPE)
    process.communicate(json_str.encode("utf-8"))


def show_file_in_vscode(filepath, **kw):
    process = subprocess.Popen(["/usr/local/bin/code", filepath])
    process.communicate()
