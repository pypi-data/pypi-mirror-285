import pymel.core.uitypes as gui
import pymel.core as pm
import cwmaya.helpers.const as k


class TextFieldControl(gui.FormLayout):

    def __init__(self):
        """
        Create the UI.
        """
        super(TextFieldControl, self).__init__()
        self.model = None
        self.label_ctl = pm.text(label="Dual", align="right", width=k.LABEL_WIDTH)
        self.field = pm.textField()

        self.attachForm(self.label_ctl, "left", k.FORM_SPACING_X)
        self.attachNone(self.label_ctl, "right")
        self.attachForm(self.label_ctl, "top", k.FORM_SPACING_Y)
        self.attachForm(self.label_ctl, "bottom", k.FORM_SPACING_Y)

        self.attachControl(self.field, "left", k.FORM_SPACING_X, self.label_ctl)
        self.attachForm(self.field, "right", k.FORM_SPACING_X)
        self.attachForm(self.field, "top", k.FORM_SPACING_Y)
        self.attachForm(self.field, "bottom", k.FORM_SPACING_Y)

    def set_label(self, label):
        """
        Set the label for the control.
        """
        self.label_ctl.setLabel(label)

    def bind(self, attribute):
        """
        Bind the UI to the given attribute.
        """
        self.field.setText(attribute.get() or "")
        self.field.changeCommand(pm.Callback(self.on_text_change, attribute))

    def on_text_change(self, attribute):
        """
        Update the attribute when the text changes.
        """
        attribute.set(self.field.getText().strip())
