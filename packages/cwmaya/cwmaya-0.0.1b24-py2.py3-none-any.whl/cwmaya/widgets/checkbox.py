import pymel.core.uitypes as gui
import pymel.core as pm
import cwmaya.helpers.const as k


class CheckboxControl(gui.FormLayout):

    def __init__(self):
        """
        Create the UI.
        """
        super(CheckboxControl, self).__init__()
        self.label_ctl = pm.text(label="None", align="right", width=k.LABEL_WIDTH)
        self.checkbox = pm.checkBox()

        self.attachForm(self.label_ctl, "left", k.FORM_SPACING_X)
        self.attachNone(self.label_ctl, "right")
        self.attachForm(self.label_ctl, "top", k.FORM_SPACING_Y)
        self.attachForm(self.label_ctl, "bottom", k.FORM_SPACING_Y)

        self.attachControl(self.checkbox, "left", k.FORM_SPACING_X, self.label_ctl)
        self.attachForm(self.checkbox, "right", k.FORM_SPACING_X)
        self.attachForm(self.checkbox, "top", k.FORM_SPACING_Y)
        self.attachForm(self.checkbox, "bottom", k.FORM_SPACING_Y)
        pm.checkBox(self.checkbox, edit=True, label="")

    def set_label(self, label):
        """
        Set the label for the control.
        """
        self.label_ctl.setLabel(label)

    def bind(self, attribute):
        """
        Bind the UI to the given attribute.
        """
        value=attribute.get() or False
        pm.checkBox(self.checkbox, edit=True, 
                    value=value,
                    changeCommand=pm.Callback(self.on_checkbox_change, attribute)
                    )
        
    def on_checkbox_change(self, attribute):
        """
        Update the attribute when the cb changes.
        """
        attribute.set(self.checkbox.getValue() or False)
