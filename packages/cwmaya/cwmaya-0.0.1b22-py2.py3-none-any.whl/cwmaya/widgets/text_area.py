import pymel.core.uitypes as gui
import pymel.core as pm
import cwmaya.helpers.const as k


class TextAreaControl(gui.FormLayout):

    def __init__(self):
        """
        Create the UI.
        """
        super(TextAreaControl, self).__init__()
        self.model = None
        self.label_ctl = pm.text(label="Dual", align="right", width=k.LABEL_WIDTH)
        self.area = pm.scrollField(wordWrap=True, editable=True)

        self.attachForm(self.label_ctl, "left", k.FORM_SPACING_X)
        self.attachNone(self.label_ctl, "right")
        self.attachForm(self.label_ctl, "top", k.FORM_SPACING_Y)
        self.attachNone(self.label_ctl, "bottom")

        self.attachControl(self.area, "left", k.FORM_SPACING_X, self.label_ctl)
        self.attachForm(self.area, "right", k.FORM_SPACING_X)
        self.attachForm(self.area, "top", k.FORM_SPACING_Y)
        self.attachForm(self.area, "bottom", k.FORM_SPACING_Y)

    def set_label(self, label):
        """
        Set the label for the control.
        """
        self.label_ctl.setLabel(label)

    def bind(self, attribute):
        """
        Bind the UI to the given attribute.
        """
        self.area.setText(attribute.get() or "")
        self.area.changeCommand(pm.Callback(self.on_text_change, attribute))
        self.area.enterCommand(pm.Callback(self.on_text_change, attribute))

    def on_text_change(self, attribute):
        """
        Update the attribute when the text changes.
        """
        attribute.set(self.area.getText().strip())
