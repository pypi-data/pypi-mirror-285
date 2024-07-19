import pymel.core.uitypes as gui
import pymel.core as pm
import cwmaya.helpers.const as k
from cwmaya.helpers import node_utils
from cwmaya.template.helpers import context
import pyperclip
import json


class ArgvControl(gui.FormLayout):

    def __init__(self):
        """
        Create the UI.
        """
        super(ArgvControl, self).__init__()
        self.header_row = None
        self.column = None
        self.add_btn = None
        self.build_ui()

    def build_ui(self):

        pm.setParent(self)

        self.label = pm.text(label="", width=10)

        self.header_row = pm.rowLayout(nc=2, adjustableColumn=1)
        self.header_text = pm.text(
            align="left",
            ebg=True,
            bgc=k.LIST_HEADER_BG,
            label=" Argv",
            height=24,
        )
        self.add_btn = pm.symbolButton(
            image="item_add.png", width=k.TRASH_COLUMN_WIDTH, height=24
        )
        pm.setParent(self)

        self.column = pm.columnLayout(adj=True)

        self.attachForm(self.label, "left", k.FORM_SPACING_X)
        self.attachNone(self.label, "right")
        self.attachForm(self.label, "top", k.FORM_SPACING_Y)
        self.attachForm(self.label, "bottom", k.FORM_SPACING_Y)

        self.attachControl(self.header_row, "left", k.FORM_SPACING_X, self.label)
        self.attachForm(self.header_row, "right", k.FORM_SPACING_X)
        self.attachForm(self.header_row, "top", k.FORM_SPACING_Y)
        self.attachNone(self.header_row, "bottom")

        self.attachControl(self.column, "left", k.FORM_SPACING_X, self.label)
        self.attachForm(self.column, "right", k.FORM_SPACING_X)
        self.attachControl(self.column, "top", 0, self.header_row)
        self.attachForm(self.column, "bottom", k.FORM_SPACING_Y)

    def bind(self, attribute):
        """
        populate the fields
        """
        pm.setParent(self.column)

        # pm.text(self.header_text, edit=True, label=attribute.attrName(longName=True))
        for widget in pm.columnLayout(self.column, q=True, childArray=True) or []:
            pm.deleteUI(widget)

        for attr_element in attribute:
            self.create_row(attr_element)

        pm.button(self.add_btn, edit=True, command=pm.Callback(self.on_add, attribute))

    def create_row(self, attr_element):
        pm.setParent(self.column)

        row = pm.rowLayout(nc=2, adjustableColumn=1)
        field_ctl = pm.textField(text=attr_element.get() or "")
        del_ctl = pm.symbolButton(image="item_delete.png", width=k.TRASH_COLUMN_WIDTH)
        pm.setParent(self.column)

        pm.symbolButton(
            del_ctl,
            edit=True,
            command=pm.Callback(self.remove_entry, attr_element, row),
        )
        field_ctl.changeCommand(
            pm.Callback(self.on_text_change, attr_element, field_ctl)
        )
        return row

    def on_text_change(self, attribute, control):
        attribute.set(control.getText())

    def remove_entry(self, attribute, control):
        pm.deleteUI(control)
        print("REMOVEMULTIINSTANCE:", attribute)
        pm.removeMultiInstance(attribute, b=True)

    def on_add(self, attribute):
        attr_element = node_utils.next_element_plug(attribute)
        attr_element.set("Some Arg")
        pm.setParent(self.column)
        self.create_row(attr_element)


class CommandsControl(gui.FormLayout):

    def __init__(self):
        """
        Create the UI.
        """
        super(CommandsControl, self).__init__()
        self.header_row = None
        self.column = None
        self.add_btn = None
        self.build_ui()

    def build_ui(self):

        pm.setParent(self)

        self.label = pm.text(label="", width=k.LABEL_WIDTH)

        self.header_row = pm.rowLayout(nc=3, adjustableColumn=1)
        pm.text(
            align="left",
            ebg=True,
            bgc=k.LIST_HEADER_BG,
            label=" Commands",
            height=24,
        )
        pm.text(
            align="center", label="Copy", height=24, width=(k.TRASH_COLUMN_WIDTH * 1.5)
        )
        self.add_btn = pm.symbolButton(
            image="item_add.png", width=k.TRASH_COLUMN_WIDTH, height=24
        )

        pm.setParent(self)
        self.column = pm.columnLayout(adj=True)

        self.attachForm(self.label, "left", k.FORM_SPACING_X)
        self.attachNone(self.label, "right")
        self.attachForm(self.label, "top", k.FORM_SPACING_Y)
        self.attachForm(self.label, "bottom", k.FORM_SPACING_Y)

        self.attachControl(self.header_row, "left", k.FORM_SPACING_X, self.label)
        self.attachForm(self.header_row, "right", k.FORM_SPACING_X)
        self.attachForm(self.header_row, "top", k.FORM_SPACING_Y)
        self.attachNone(self.header_row, "bottom")

        self.attachControl(self.column, "left", k.FORM_SPACING_X, self.label)
        self.attachForm(self.column, "right", k.FORM_SPACING_X)
        self.attachControl(self.column, "top", 0, self.header_row)
        self.attachForm(self.column, "bottom", k.FORM_SPACING_Y)

    def bind(self, attribute):
        """
        populate the metadata controls
        """
        pm.setParent(self.column)
        for widget in pm.columnLayout(self.column, q=True, childArray=True) or []:
            pm.deleteUI(widget)

        for attr_element in attribute:
            self.create_row(attr_element)

        pm.button(self.add_btn, edit=True, command=pm.Callback(self.on_add, attribute))

    def create_row(self, attr_element):

        argv_attr = attr_element.children()[0]
        pm.setParent(self.column)

        frame = pm.frameLayout(
            label=attr_element.longName(),
            collapsable=True,
            collapse=False,
            borderVisible=True,
        )
        form = pm.formLayout()

        argv_control = ArgvControl()
        pm.setParent(form)
        clipboard_ctl = pm.symbolButton(
            image="gotoLine.png",
            width=(k.TRASH_COLUMN_WIDTH * 1.5),
            ann="Copy to clipboard",
        )
        del_ctl = pm.symbolButton(image="item_delete.png", width=k.TRASH_COLUMN_WIDTH)

        pm.symbolButton(
            del_ctl,
            edit=True,
            command=pm.Callback(self.remove_entry, attr_element, frame),
        )

        pm.symbolButton(
            clipboard_ctl,
            edit=True,
            command=pm.Callback(self.copy_command_to_clipboard, argv_attr),
        )

        form.attachNone(del_ctl, "left")
        form.attachForm(del_ctl, "right", 0)
        form.attachForm(del_ctl, "top", 0)
        form.attachNone(del_ctl, "bottom")

        form.attachNone(clipboard_ctl, "left")
        form.attachControl(clipboard_ctl, "right", 0, del_ctl)
        form.attachForm(clipboard_ctl, "top", 0)
        form.attachNone(clipboard_ctl, "bottom")

        form.attachForm(argv_control, "left", 0)
        form.attachControl(argv_control, "right", 0, clipboard_ctl)
        form.attachForm(argv_control, "top", 0)
        form.attachForm(argv_control, "bottom", 0)

        argv_control.bind(argv_attr)

        return frame

    def remove_entry(self, attribute, control):
        pm.deleteUI(control)
        pm.removeMultiInstance(attribute, b=True)

    def on_add(self, attribute):
        attr_element = node_utils.next_element_plug(attribute)
        attr_element.set([])
        pm.setParent(self.column)
        self.create_row(attr_element)

    def copy_command_to_clipboard(self, argv_attr):
        node = pm.PyNode(argv_attr).node()
        tokensAttr = node.attr("tokens")
        pm.dgdirty(tokensAttr)
        tokens = json.loads(tokensAttr.get())

        argv = [context.interpolate(arg.get(), tokens) for arg in argv_attr]
        joined = " ".join(argv)
        pyperclip.copy(joined)
        print(f"Command copied to clipboard:")
        print(joined)
