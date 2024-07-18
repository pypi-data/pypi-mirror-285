import pymel.core.uitypes as gui
import pymel.core as pm
import cwmaya.helpers.const as k
from cwmaya.helpers import node_utils
from cwmaya.template.helpers import context
import pyperclip
import json


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

        self.add_btn = pm.symbolButton(
            image="item_add.png", width=k.TRASH_COLUMN_WIDTH, height=24
        )

        self.header_row = _form_layout(
            pm.text(
                align="left",
                ebg=True,
                bgc=k.LIST_HEADER_BG,
                label=" Command",
                height=24,
            ),
            pm.text(
                align="center",
                # ebg=True,
                # bgc=k.LIST_HEADER_BG,
                label="Copy",
                height=24,
                width=(k.TRASH_COLUMN_WIDTH*1.5)
            ),
            self.add_btn,
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
        pm.setParent(self.column)
        # key_attr, value_attr = attr_element.getChildren()

        field_ctl = pm.textField(text=attr_element.get() or "")
        clipboard_ctl = pm.symbolButton( image="gotoLine.png", width=(k.TRASH_COLUMN_WIDTH*1.5),  ann="Copy to clipboard")
        del_ctl = pm.symbolButton(image="item_delete.png", width=k.TRASH_COLUMN_WIDTH)
        row = _form_layout(field_ctl, clipboard_ctl, del_ctl)
        pm.symbolButton(
            del_ctl,
            edit=True,
            command=pm.Callback(self.remove_entry, attr_element, row),
        )
        pm.symbolButton(
            clipboard_ctl,
            edit=True,
            command=pm.Callback(self.copy_command_to_clipboard, attr_element)
        )
        field_ctl.changeCommand(
            pm.Callback(self.on_text_change, attr_element, field_ctl)
        )

        return row

    def on_text_change(self, attribute, control):
        attribute.set(control.getText())

    def remove_entry(self, attribute, control):
        pm.deleteUI(control)
        pm.removeMultiInstance(attribute, b=True)

    def on_add(self, attribute):
        attr_element = node_utils.next_element_plug(attribute)
        attr_element.set("Some Command")
        pm.setParent(self.column)
        self.create_row(attr_element)
    
    def copy_command_to_clipboard(self, attr_element):
        node = pm.PyNode(attr_element).node()
        tokensAttr = node.attr("tokens")
        pm.dgdirty(tokensAttr)
        tokens = json.loads(tokensAttr.get())
        text = attr_element.get()
        resolved = context.interpolate(text, tokens)
        pyperclip.copy(resolved)
        print(f"Command copied to clipboard:")
        print(resolved)
        


def _form_layout(*widgets, **kwargs):

    form = pm.formLayout(nd=100)
    for widget in widgets:
        pm.control(widget, edit=True, parent=form)

    form.attachForm(widgets[0], "left", k.FORM_SPACING_X)
    form.attachControl(widgets[0], "right", k.FORM_SPACING_X, widgets[1])
    form.attachForm(widgets[0], "top", k.FORM_SPACING_Y)
    form.attachForm(widgets[0], "bottom", k.FORM_SPACING_Y)

    form.attachNone(widgets[1], "left")
    form.attachControl(widgets[1], "right", k.FORM_SPACING_X, widgets[2])
    form.attachForm(widgets[2], "top", k.FORM_SPACING_Y)
    form.attachForm(widgets[2], "bottom", k.FORM_SPACING_Y)

    form.attachNone(widgets[2], "left")
    form.attachForm(widgets[2], "right", k.FORM_SPACING_X)
    form.attachForm(widgets[2], "top", k.FORM_SPACING_Y)
    form.attachForm(widgets[2], "bottom", k.FORM_SPACING_Y)

    return form
