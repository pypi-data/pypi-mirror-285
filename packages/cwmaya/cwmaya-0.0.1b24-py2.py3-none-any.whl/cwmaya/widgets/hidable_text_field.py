import pymel.core.uitypes as gui
import pymel.core as pm
import cwmaya.helpers.const as k


class HidableTextFieldControl(gui.FormLayout):

    def __init__(self):
        """
        Create the UI.
        """
        super(HidableTextFieldControl, self).__init__()
        self.model = None
        self.label_ctl = pm.text(label="Dual", align="right", width=k.LABEL_WIDTH)
        self.switch = pm.checkBox(label="")
        self.field = pm.textField()

        self.attachForm(self.label_ctl, "left", k.FORM_SPACING_X)
        self.attachNone(self.label_ctl, "right")
        self.attachForm(self.label_ctl, "top", k.FORM_SPACING_Y)
        self.attachForm(self.label_ctl, "bottom", k.FORM_SPACING_Y)

        self.attachControl(self.switch, "left", k.FORM_SPACING_X, self.label_ctl)
        self.attachNone(self.switch, "right")
        self.attachForm(self.switch, "top", k.FORM_SPACING_Y)
        self.attachForm(self.switch, "bottom", k.FORM_SPACING_Y)

        self.attachControl(self.field, "left", k.FORM_SPACING_X, self.switch)
        self.attachForm(self.field, "right", k.FORM_SPACING_X)
        self.attachForm(self.field, "top", k.FORM_SPACING_Y)
        self.attachForm(self.field, "bottom", k.FORM_SPACING_Y)
        self.setHeight(24)

    def set_label(self, label):
        """
        Set the label for the control.
        """
        self.label_ctl.setLabel(label)

    def bind(self, switch_attribute, text_attribute):
        """
        Bind the UI to the given attribute.
        """
        self.switch.setValue(switch_attribute.get() or False)
        self.field.setText(text_attribute.get() or "")
        self.on_switch_change(switch_attribute)
        self.switch.setChangeCommand(
            pm.Callback(self.on_switch_change, switch_attribute)
        )
        self.field.changeCommand(pm.Callback(self.on_text_change, text_attribute))

    def on_text_change(self, attribute):
        """
        Update the attribute when the text changes.
        """
        attribute.set(self.field.getText().strip())

    def on_switch_change(self, attribute):
        """
        Update the attribute when the text changes.
        """
        value = self.switch.getValue()
        attribute.set(value)
        self.field.setVisible(value)
