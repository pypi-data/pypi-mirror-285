import pymel.core.uitypes as gui
import pymel.core as pm
import os
import cwmaya.helpers.const as k
from cwmaya.helpers import node_utils

import pyperclip


class ScriptControl(gui.FormLayout):

    def __init__(self):
        """
        Create the UI.
        """
        super(ScriptControl, self).__init__()
        # self.script_name_layout = None # name and checkbox
        self.use_script_cb = None
        self.script_name_tf = None
        self.scene_tf = None

        # self.args_layout = None  # args and args type dropdown and add button
        self.arg_type_dropdown = None
        self.args_column = None
        self.add_arg_btn = None

        self.kwargs_column = None
        self.add_kwarg_btn = None

        self.name_layout = None  # name and checkbox
        self.args_layout = None  # args UI
        self.kwargs_layout = None  # kwargs UI

        self.clipboard_btn = None

        self.build_ui()

    def build_ui(self):
        pm.setParent(self)

        use_script_row = pm.rowLayout(nc=2)
        pm.text(width=k.LABEL_WIDTH, align="right", label="Use script ")
        self.use_script_cb = pm.checkBox(label="")
        pm.setParent(self)

        self.name_layout = self.build_top_layout()
        pm.setParent(self)
        self.args_layout = self.build_args_layout()
        pm.setParent(self)
        self.kwargs_layout = self.build_kwargs_layout()

        self.attachForm(use_script_row, "left", k.FORM_SPACING_X)
        self.attachForm(use_script_row, "right", k.FORM_SPACING_X)
        self.attachForm(use_script_row, "top", k.FORM_SPACING_Y)
        self.attachNone(use_script_row, "bottom")

        self.attachForm(self.name_layout, "left", k.FORM_SPACING_X)
        self.attachForm(self.name_layout, "right", k.FORM_SPACING_X)
        self.attachControl(self.name_layout, "top", k.FORM_SPACING_Y, use_script_row)
        self.attachNone(self.name_layout, "bottom")

        self.attachForm(self.args_layout, "left", k.FORM_SPACING_X)
        self.attachForm(self.args_layout, "right", k.FORM_SPACING_X)
        self.attachControl(self.args_layout, "top", 0, self.name_layout)
        self.attachNone(self.args_layout, "bottom")

        self.attachForm(self.kwargs_layout, "left", k.FORM_SPACING_X)
        self.attachForm(self.kwargs_layout, "right", k.FORM_SPACING_X)
        self.attachControl(self.kwargs_layout, "top", 0, self.args_layout)
        self.attachForm(self.kwargs_layout, "bottom", k.FORM_SPACING_Y)

    def build_top_layout(self):

        col = pm.columnLayout(adj=True)
        pm.setParent(col)
        pm.rowLayout(nc=3, adjustableColumn=2)
        pm.text(width=k.LABEL_WIDTH, align="right", label="Script name")
        self.script_name_tf = pm.textField(width=200)
        self.clipboard_btn = pm.symbolButton(
            image="gotoLine.png",
            width=k.TRASH_COLUMN_WIDTH,
            height=24,
            ann="Copy to clipboard",
        )
        pm.setParent(col)
        pm.rowLayout(nc=3, adjustableColumn=2)
        pm.text(width=k.LABEL_WIDTH, align="right", label="Scene")
        self.scene_tf = pm.textField(width=200)
        pm.text(label="" , width=k.TRASH_COLUMN_WIDTH)
        pm.setParent(col)

        return col

    def build_args_layout(self):
        args_form = pm.formLayout(nd=100)

        label = pm.text(
            width=k.LABEL_WIDTH, align="right", label="Positional args type"
        )
        self.arg_type_dropdown = pm.optionMenu(width=k.LABEL_WIDTH * 2, height=24)
        pm.setParent(self.arg_type_dropdown, menu=True)
        for arg_type in k.DATATYPES:
            pm.menuItem(label=arg_type)

        pm.setParent(args_form)
        self.add_arg_btn = pm.symbolButton(
            image="item_add.png", width=k.TRASH_COLUMN_WIDTH, height=24
        )

        self.args_column = pm.columnLayout(adj=True)

        args_form.attachForm(label, "left", k.FORM_SPACING_X)
        args_form.attachNone(label, "right")
        args_form.attachForm(label, "top", k.FORM_SPACING_Y)
        args_form.attachNone(label, "bottom")

        args_form.attachNone(self.arg_type_dropdown, "left")
        args_form.attachForm(self.add_arg_btn, "right", k.FORM_SPACING_X)
        args_form.attachForm(self.add_arg_btn, "top", k.FORM_SPACING_Y)
        args_form.attachNone(self.add_arg_btn, "bottom")

        args_form.attachControl(self.arg_type_dropdown, "left", k.FORM_SPACING_X, label)
        args_form.attachNone(self.arg_type_dropdown, "right")
        args_form.attachForm(self.arg_type_dropdown, "top", k.FORM_SPACING_Y)
        args_form.attachNone(self.arg_type_dropdown, "bottom")

        args_form.attachForm(self.args_column, "left", k.FORM_SPACING_X)
        args_form.attachForm(self.args_column, "right", k.FORM_SPACING_X)
        args_form.attachControl(self.args_column, "top", 0, self.arg_type_dropdown)
        args_form.attachForm(self.args_column, "bottom", k.FORM_SPACING_Y)

        return args_form

    def build_kwargs_layout(self):
        kwargs_form = pm.formLayout(nd=100)

        pm.setParent(kwargs_form)
        label = pm.text(label="Keyword args", width=k.LABEL_WIDTH, align="right")
        self.kwargs_column = pm.columnLayout(adj=True)
        pm.setParent(kwargs_form)

        self.add_kwarg_btn = pm.symbolButton(
            image="item_add.png", width=k.TRASH_COLUMN_WIDTH, height=24
        )
        pm.setParent(kwargs_form)

        kwargs_header_row = _kwarg_form_layout(
            pm.text(
                width=(k.LABEL_WIDTH * 1.5),
                align="left",
                ebg=True,
                bgc=k.LIST_HEADER_BG,
                label=" Keyword",
                height=24,
            ),
            pm.text(
                align="left",
                ebg=True,
                bgc=k.LIST_HEADER_BG,
                label=" Value",
                height=24,
            ),
            pm.text(
                align="left",
                width=(k.LABEL_WIDTH),
                ebg=True,
                bgc=k.LIST_HEADER_BG,
                label=" Type",
                height=24,
            ),
            self.add_kwarg_btn,
        )
        pm.setParent(kwargs_form)

        kwargs_form.attachForm(label, "left", k.FORM_SPACING_X)
        kwargs_form.attachNone(label, "right")
        kwargs_form.attachForm(label, "top", k.FORM_SPACING_Y)
        kwargs_form.attachNone(label, "bottom")

        kwargs_form.attachControl(kwargs_header_row, "left", k.FORM_SPACING_X, label)
        kwargs_form.attachForm(kwargs_header_row, "right", k.FORM_SPACING_X)
        kwargs_form.attachForm(kwargs_header_row, "top", k.FORM_SPACING_Y)
        kwargs_form.attachNone(kwargs_header_row, "bottom")

        kwargs_form.attachControl(self.kwargs_column, "left", k.FORM_SPACING_X, label)
        kwargs_form.attachForm(self.kwargs_column, "right", k.FORM_SPACING_X)
        kwargs_form.attachControl(self.kwargs_column, "top", 0, kwargs_header_row)
        kwargs_form.attachForm(self.kwargs_column, "bottom", k.FORM_SPACING_Y)

        return kwargs_form

    def bind(self, node, prefix, use_script_changed=None):
        """
        populate the controls
        """
        self.use_script_callback = use_script_changed
        
        self.bind_use_script(
            node,
            prefix,
        )
        
        self.bind_script(node, prefix)
        self.bind_scene(node, prefix)
        self.bind_args(node, prefix)
        self.bind_kwargs(node, prefix)

        pm.button(
            self.clipboard_btn,
            edit=True,
            command=pm.Callback(self.copy_script_to_clipboard, node, prefix),
        )

    ################ Use Script ################
    def bind_use_script(self, node, prefix):
        use_script_attribute = node.attr(prefix + "UseScript")
        use_script_value = use_script_attribute.get() or False
        pm.checkBox(
            self.use_script_cb,
            edit=True,
            value=use_script_value,
            changeCommand=pm.Callback(self.on_use_script_change, use_script_attribute),
        )
        if self.use_script_callback:
            self.use_script_callback(use_script_value)

    def on_use_script_change(self, attribute):
        use_script = self.use_script_cb.getValue()
        if self.use_script_callback:
            self.use_script_callback(use_script)

        self.name_layout.setEnable(use_script)
        self.args_layout.setEnable(use_script)
        self.kwargs_layout.setEnable(use_script)

        attribute.set(self.use_script_cb.getValue() or False)

    ################ Script Name ################
    def bind_script(self, node, prefix):
        script_attribute = node.attr(prefix + "Script")
        self.script_name_tf.setText(script_attribute.get() or "")
        self.script_name_tf.changeCommand(
            pm.Callback(self.on_script_change, script_attribute)
        )
        
    def bind_scene(self, node, prefix):
        scene_attribute = node.attr(prefix + "Scene")
        self.scene_tf.setText(scene_attribute.get() or "")
        self.scene_tf.changeCommand(
            pm.Callback(self.on_scene_change, scene_attribute)
        )
  
    def on_script_change(self, attribute):
        attribute.set(self.script_name_tf.getText().strip())

    def on_scene_change(self, attribute):
        attribute.set(self.scene_tf.getText().strip())


    ################ Args ################
    def bind_args(self, node, prefix):
        args_type_attribute = node.attr(prefix + "ArgsType")
        value = args_type_attribute.get()
        pm.optionMenu(
            self.arg_type_dropdown,
            edit=True,
            select=(value + 1),
            changeCommand=pm.Callback(self.on_args_type_change, args_type_attribute),
        )
        args_attribute = node.attr(prefix + "Args")

        for attr_element in args_attribute:
            self.create_arg_row(attr_element)

        pm.button(
            self.add_arg_btn,
            edit=True,
            command=pm.Callback(self.on_add_arg, args_attribute),
        )

    def on_args_type_change(self, attribute):
        selected_index = self.arg_type_dropdown.getSelect()
        attribute.set(selected_index - 1)

    def on_add_arg(self, attribute):
        attr_element = node_utils.next_element_plug(attribute)
        attr_element.set("arg_value")
        pm.setParent(self.args_column)
        self.create_arg_row(attr_element)

    def create_arg_row(self, attr_element):
        pm.setParent(self.args_column)

        label_ctl = pm.text(width=k.LABEL_WIDTH, align="right", label=" Arg")

        field_ctl = pm.textField(text=attr_element.get() or "")
        del_ctl = pm.symbolButton(image="item_delete.png", width=k.TRASH_COLUMN_WIDTH)
        row = _arg_form_layout(label_ctl, field_ctl, del_ctl)
        pm.symbolButton(
            del_ctl,
            edit=True,
            command=pm.Callback(self.remove_entry, attr_element, row),
        )
        field_ctl.changeCommand(
            pm.Callback(self.on_text_change, attr_element, field_ctl)
        )
        return row

    ################ Kwargs ################
    def bind_kwargs(self, node, prefix):
        pm.setParent(self.kwargs_column)

        kwargs_attribute = node.attr(prefix + "Kwargs")
        for widget in (
            pm.columnLayout(self.kwargs_column, q=True, childArray=True) or []
        ):
            pm.deleteUI(widget)
        for attr_element in kwargs_attribute:
            self.create_kwarg_row(attr_element)
        pm.button(
            self.add_kwarg_btn,
            edit=True,
            command=pm.Callback(self.on_add_kwarg, kwargs_attribute),
        )

    def create_kwarg_row(self, attr_element):
        pm.setParent(self.kwargs_column)
        key_attr, value_attr, type_attr = attr_element.getChildren()

        key_ctl = pm.textField(text=key_attr.get(), width=k.LABEL_WIDTH)
        value_ctl = pm.textField(text=value_attr.get())
        type_ctl = pm.optionMenu(width=k.LABEL_WIDTH)
        pm.setParent(type_ctl, menu=True)
        for arg_type in k.DATATYPES:
            pm.menuItem(label=arg_type)
        type_ctl.setSelect(type_attr.get() + 1)

        pm.setParent(self.kwargs_column)
        del_ctl = pm.symbolButton(image="item_delete.png", width=k.TRASH_COLUMN_WIDTH)

        row = _kwarg_form_layout(key_ctl, value_ctl, type_ctl, del_ctl)
        pm.symbolButton(
            del_ctl,
            edit=True,
            command=pm.Callback(self.remove_entry, attr_element, row),
        )
        key_ctl.changeCommand(pm.Callback(self.on_text_change, key_attr, key_ctl))
        value_ctl.changeCommand(pm.Callback(self.on_text_change, value_attr, value_ctl))
        type_ctl.changeCommand(pm.Callback(self.on_enum_change, type_attr, type_ctl))
        return row

    def on_add_kwarg(self, attribute):
        attr_element = node_utils.next_element_plug(attribute)
        key_attribute, value_attribute, type_attribute = attr_element.getChildren()

        key_attribute.set("kwarg_name")
        value_attribute.set("kwarg_value")
        type_attribute.set(1)

        pm.setParent(self.kwargs_column)
        self.create_kwarg_row(attr_element)

    ################################

    def on_text_change(self, attribute, control):
        attribute.set(control.getText())

    def on_enum_change(self, attribute, control):
        attribute.set(control.getSelect() - 1)

    def remove_entry(self, attribute, control):
        pm.deleteUI(control)
        pm.removeMultiInstance(attribute, b=True)

    def copy_script_to_clipboard(self, node, prefix):
        outattr = node.attr(prefix + "OutScript")
        pm.dgdirty(outattr)
        script = outattr.get()
        cwmodpath = pm.moduleInfo(path=True, moduleName="coreweave")
        stormmodpath = os.path.join(os.path.dirname(cwmodpath), "storm_remote")
        mayabinpath = os.path.join(os.environ.get("MAYA_LOCATION"), "bin")
        script = f'MAYA_MODULE_PATH="{stormmodpath}" PATH="$PATH:{mayabinpath}" {script}'
        pyperclip.copy(script)
        print("Script copied to clipboard")
        print(script)


def _kwarg_form_layout(*widgets, **kwargs):

    form = pm.formLayout(nd=100)
    for widget in widgets:
        pm.control(widget, edit=True, parent=form)

    form.attachForm(widgets[0], "left", k.FORM_SPACING_X)
    form.attachNone(widgets[0], "right")
    form.attachForm(widgets[0], "top", k.FORM_SPACING_Y)
    form.attachForm(widgets[0], "bottom", k.FORM_SPACING_Y)

    form.attachControl(widgets[1], "left", k.FORM_SPACING_X, widgets[0])
    form.attachControl(widgets[1], "right", k.FORM_SPACING_X, widgets[2])
    form.attachForm(widgets[1], "top", k.FORM_SPACING_Y)
    form.attachForm(widgets[1], "bottom", k.FORM_SPACING_Y)

    form.attachNone(widgets[2], "left")
    form.attachControl(widgets[2], "right", k.FORM_SPACING_X, widgets[3])
    form.attachForm(widgets[2], "top", k.FORM_SPACING_Y)
    form.attachForm(widgets[2], "bottom", k.FORM_SPACING_Y)

    form.attachNone(widgets[3], "left")
    form.attachForm(widgets[3], "right", k.FORM_SPACING_X)
    form.attachForm(widgets[3], "top", k.FORM_SPACING_Y)
    form.attachForm(widgets[3], "bottom", k.FORM_SPACING_Y)

    return form


def _arg_form_layout(*widgets, **kwargs):

    form = pm.formLayout(nd=100)
    for widget in widgets:
        pm.control(widget, edit=True, parent=form)

    form.attachForm(widgets[0], "left", k.FORM_SPACING_X)
    form.attachNone(widgets[0], "right")
    form.attachForm(widgets[0], "top", k.FORM_SPACING_X)
    form.attachForm(widgets[0], "bottom", k.FORM_SPACING_Y)

    form.attachControl(widgets[1], "left", k.FORM_SPACING_X, widgets[0])
    form.attachControl(widgets[1], "right", k.FORM_SPACING_X, widgets[2])
    form.attachForm(widgets[1], "top", k.FORM_SPACING_Y)
    form.attachForm(widgets[1], "bottom", k.FORM_SPACING_Y)

    form.attachNone(widgets[2], "left")
    form.attachForm(widgets[2], "right", k.FORM_SPACING_X)
    form.attachForm(widgets[2], "top", k.FORM_SPACING_Y)
    form.attachForm(widgets[2], "bottom", k.FORM_SPACING_Y)

    return form
