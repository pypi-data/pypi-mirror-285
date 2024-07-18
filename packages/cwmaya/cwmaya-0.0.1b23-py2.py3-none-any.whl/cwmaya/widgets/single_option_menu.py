# -*- coding: utf-8 -*-

import pymel.core.uitypes as gui
import pymel.core as pm
import cwmaya.helpers.const as k


class SingleOptionMenuControl(gui.FormLayout):

    def __init__(self):
        """
        Create the UI.
        """
        super(SingleOptionMenuControl, self).__init__()
        self.model = None
        self.attribute = None
        self.label_ctl = pm.text(label="Something", align="right", width=k.LABEL_WIDTH)
        self.content_menu = pm.optionMenu()

        self.attachForm(self.label_ctl, "left", k.FORM_SPACING_X)
        self.attachNone(self.label_ctl, "right")
        self.attachForm(self.label_ctl, "top", k.FORM_SPACING_Y)
        self.attachForm(self.label_ctl, "bottom", k.FORM_SPACING_Y)

        self.attachControl(self.content_menu, "left", k.FORM_SPACING_X, self.label_ctl)
        self.attachForm(self.content_menu, "right", k.FORM_SPACING_X)
        self.attachForm(self.content_menu, "top", k.FORM_SPACING_Y)
        self.attachForm(self.content_menu, "bottom", k.FORM_SPACING_Y)

    def set_label(self, label):
        """
        Set the label for the control.
        """

        self.label_ctl.setLabel(label)

    def bind(self, attribute):
        """
        Bind the UI to the given attribute.
        """
        self.attribute = attribute

        self.content_menu.changeCommand(pm.Callback(self.on_content_menu_change))
        self.hydrate(k.UNCONNECTED_MODEL)

    def hydrate(self, model):
        """
        Populate the menu.
        """
        self.model = model

        pm.setParent(self.content_menu, menu=True)
        self.content_menu.clear()
        for item in self.model:
            pm.menuItem(label=item["description"])

        if self.is_unconnected_model():
            return

        attr_value = self.attribute.get()
        entry = self._find_item(attr_value)
        if not entry:
            entry = self.model[0]
            self.attribute.set(entry["name"])
        self.content_menu.setValue(entry["description"])

    def on_content_menu_change(self):
        description = self.content_menu.getValue()
        name = self._find_item(description)["name"]
        self.attribute.set(name)

    def _find_item(self, name_or_description):
        """
        Get the name for the given display content description.
        """
        for item in self.model:
            if name_or_description in [item["name"], item["description"]]:
                return item
        return None

    def is_unconnected_model(self):
        """
        Checks whether the current model is in a 'not connected' state, indicated by a specific placeholder description.

        Returns:
            True if the model is in the 'not connected' state, False otherwise.
        """
        return self.model[0]["description"] == k.UNCONNECTED_MODEL[0]["description"]
