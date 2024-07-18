import pymel.core.uitypes as gui
import pymel.core as pm
import cwmaya.helpers.const as k


class DualOptionMenuControl(gui.FormLayout):

    def __init__(self):
        """
        Create the UI.
        """
        super(DualOptionMenuControl, self).__init__()
        self.model = None
        self.attribute = None
        self.label_ctl = pm.text(label="Dual", align="right", width=k.LABEL_WIDTH)
        self.category_menu = pm.optionMenu()
        self.content_menu = pm.optionMenu()

        self.attachForm(self.label_ctl, "left", k.FORM_SPACING_X)
        self.attachNone(self.label_ctl, "right")
        self.attachForm(self.label_ctl, "top", k.FORM_SPACING_Y)
        self.attachForm(self.label_ctl, "bottom", k.FORM_SPACING_Y)

        self.attachControl(self.category_menu, "left", k.FORM_SPACING_X, self.label_ctl)
        self.attachPosition(self.category_menu, "right", k.FORM_SPACING_X, 30)
        self.attachForm(self.category_menu, "top", k.FORM_SPACING_Y)
        self.attachForm(self.category_menu, "bottom", k.FORM_SPACING_Y)

        self.attachControl(
            self.content_menu, "left", k.FORM_SPACING_X, self.category_menu
        )
        self.attachForm(self.content_menu, "right", k.FORM_SPACING_X)
        self.attachForm(self.content_menu, "top", k.FORM_SPACING_Y)
        self.attachForm(self.content_menu, "bottom", k.FORM_SPACING_Y)

    def set_label(self, label):
        """
        Set the label for the control.
        """
        self.label_ctl.setLabel(label)

    def hydrate(self, model):
        """
        Populate the option menus with a model and set to [0][0].
        """
        self.model = model

        self.category_menu.clear()
        self.content_menu.clear()

        pm.setParent(self.category_menu, menu=True)
        if self.is_unconnected_model():
            self._hydrate_not_connected_model()
            return

        for category in self.model:
            pm.menuItem(label=category["label"])

        attr_value = self.attribute.get()
        category = self._find_category(name_or_description=attr_value)
        if not category:
            category = self.model[0]
            content = category["content"][0]
            attr_value = content["name"]
            self.attribute.set(attr_value)

        self.category_menu.setValue(category["label"])
        self._hydrate_content(category)

    def _hydrate_content(self, category):
        """
        Populate the content menu.

        If the category is not found, the first category will be used.
        """
        pm.setParent(self.content_menu, menu=True)
        self.content_menu.clear()
        for item in category["content"]:
            pm.menuItem(label=item["description"])

        attr_value = self.attribute.get()
        content_entry = self._find_item(attr_value, category["label"])
        if not content_entry:
            content_entry = category["content"][0]
            attr_value = content_entry["name"]
            self.attribute.set(attr_value)
        self.content_menu.setValue(content_entry["description"])

    def _hydrate_not_connected_model(self):
        pm.setParent(self.category_menu, menu=True)
        pm.menuItem(label=k.UNCONNECTED_DUAL_MODEL[0]["label"])
        pm.setParent(self.content_menu, menu=True)
        pm.menuItem(label=k.UNCONNECTED_DUAL_MODEL[0]["content"][0]["description"])

    def bind(self, attribute):
        """
        Bind the UI to the given attribute.
        """
        self.attribute = attribute

        # bind the change commands to the attribute
        self.category_menu.changeCommand(pm.Callback(self._on_category_menu_change))
        self.content_menu.changeCommand(pm.Callback(self._on_content_menu_change))
        self.hydrate(k.UNCONNECTED_DUAL_MODEL)

    def _on_category_menu_change(self):
        label = self.category_menu.getValue()
        category = self._find_category(label=label)
        self._hydrate_content(category)

    def _on_content_menu_change(self):
        description = self.content_menu.getValue()
        category_label = self.category_menu.getValue()
        content_name = self._find_item(description, category_label)["name"]
        self.attribute.set(content_name)

    def _find_item(self, name_or_description, category_label=None):
        """
        Get the name for the given display content description.
        """
        if not category_label:
            for category in self.model:
                for item in category["content"]:
                    if name_or_description in [item["name"], item["description"]]:
                        return item
        else:
            category = next(
                (c for c in self.model if c["label"] == category_label), None
            )
            if category:
                for item in category["content"]:
                    if name_or_description in [item["name"], item["description"]]:
                        return item
        return None

    def _find_category(self, name_or_description=None, label=None):
        """
        Find the category with the given name or description.
        """
        if name_or_description:
            for category in self.model:
                for item in category["content"]:
                    if name_or_description in [item["name"], item["description"]]:
                        return category
        elif label:
            for category in self.model:
                if category["label"] == label:
                    return category
        return None

    def is_unconnected_model(self):
        """
        Checks whether the current model is in a 'not connected' state, indicated by a specific placeholder description.

        Returns:
            True if the model is in the 'not connected' state, False otherwise.
        """

        return (
            self.model[0]["label"] == k.UNCONNECTED_DUAL_MODEL[0]["label"]
            and self.model[0]["content"][0]["description"]
            == k.UNCONNECTED_DUAL_MODEL[0]["content"][0]["description"]
        )
