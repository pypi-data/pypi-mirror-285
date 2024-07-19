# -*- coding: utf-8 -*-

"""
This module defines a user interface for managing software stacks within Maya. It provides functionality to bind UI controls to specific attributes and hydrate (populate) those controls based on the model data.

Binding associates the control with an attribute and it can be assumed that by the time any hydration happens, the control has already been bound. We never bind twice, and we never hydrate before binding.

Hydration can happen several times. The user may reconnect to Conductor due to new software coming online, or due to a change of orchestrator. Hydration attempts to preserve the current values of attributes. However, it ensures that the attributes are in the model, defaulting to predefined model values if necessary.

The UI supports dynamic addition and removal of entries for both host software and plugins.
"""

import pymel.core.uitypes as gui
import pymel.core as pm
import cwmaya.helpers.const as k
from cwmaya.helpers import node_utils


class SoftwareStackControl(gui.FormLayout):
    """
    A custom form layout control designed to manage a stack of software configurations including hosts and their associated plugins.

    Attributes:
        model (dict): The data model containing host and plugin information.
        attribute: The Maya attribute to which this control is bound.
        header_row: The row layout for headers (unused).
        host_label_ctl: The label control for the host software.
        host_menu: The option menu control for selecting a host.
        plugins_column: The column layout for listing plugins.
        add_btn: The button control for adding new plugin entries.
    """

    def __init__(self):
        """
        Initializes the SoftwareStackControl instance, creating its UI components.
        """
        super(SoftwareStackControl, self).__init__()
        self.model = None
        self.attribute = None
        self.header_row = None

        self.host_label_ctl = None
        self.host_menu = None

        self.plugins_column = None
        self.add_btn = None
        self.build_ui()

    def build_ui(self):
        """
        Constructs the UI elements for the software stack control and sets up their layout.
        """
        pm.setParent(self)

        self.host_label_ctl = pm.text(
            label="Host software", align="right", width=k.LABEL_WIDTH
        )
        self.host_menu = pm.optionMenu()

        self.add_btn = pm.symbolButton(
            image="item_add.png", width=k.TRASH_COLUMN_WIDTH, height=24
        )

        self.plugins_label = pm.text(label="", align="right", width=k.LABEL_WIDTH)
        self.plugins_column = pm.columnLayout(adj=True)

        pm.setParent(self)

        self.attachForm(self.host_label_ctl, "left", k.FORM_SPACING_X)
        self.attachNone(self.host_label_ctl, "right")
        self.attachForm(self.host_label_ctl, "top", k.FORM_SPACING_Y)
        self.attachNone(self.host_label_ctl, "bottom")

        self.attachNone(self.add_btn, "left")
        self.attachForm(self.add_btn, "right", k.FORM_SPACING_X)
        self.attachForm(self.add_btn, "top", k.FORM_SPACING_Y)
        self.attachNone(self.add_btn, "bottom")

        self.attachControl(
            self.host_menu, "left", k.FORM_SPACING_X, self.host_label_ctl
        )
        self.attachControl(self.host_menu, "right", k.FORM_SPACING_X, self.add_btn)
        self.attachForm(self.host_menu, "top", k.FORM_SPACING_Y)
        self.attachNone(self.host_menu, "bottom")

        self.attachForm(self.plugins_label, "left", k.FORM_SPACING_X)
        self.attachNone(self.plugins_label, "right")
        self.attachControl(self.plugins_label, "top", k.FORM_SPACING_Y, self.host_menu)
        self.attachNone(self.plugins_label, "bottom")

        self.attachControl(
            self.plugins_column, "left", k.FORM_SPACING_X, self.plugins_label
        )
        self.attachForm(self.plugins_column, "right", k.FORM_SPACING_X)
        self.attachControl(self.plugins_column, "top", 0, self.host_menu)
        self.attachForm(self.plugins_column, "bottom", k.FORM_SPACING_Y)

        ##########################################

    def remove_entry(self, attribute, control):
        """
        Removes a specified entry from the UI and the corresponding attribute.

        Args:
            attribute: The attribute associated with the entry to be removed.
            control: The UI control representing the entry to be removed.
        """
        pm.deleteUI(control)
        pm.removeMultiInstance(attribute, b=True)

    def on_add_entry(self):
        """
        Callback function that adds a new entry to the software stack control.
        """
        host = self._find_host(self.host_menu.getValue())
        plugins = host and "plugins" in host and host["plugins"]
        if not plugins:
            return

        attr_element = node_utils.next_element_plug(self.attribute)
        attr_element.set(plugins[0]["name"])
        self.create_row(attr_element)

    def create_row(self, attr_element):
        """
        Creates a new row in the plugin column for a given attribute element.

        Args:
            attr_element: The attribute element for which to create the row.

        Returns:
            The newly created form layout for the row.
        """
        pm.setParent(self.plugins_column)
        plugin_menu = pm.optionMenu()
        del_ctl = pm.symbolButton(image="item_delete.png", width=k.TRASH_COLUMN_WIDTH)
        row = _form_layout(plugin_menu, del_ctl)
        pm.symbolButton(
            del_ctl,
            edit=True,
            command=pm.Callback(self.remove_entry, attr_element, row),
        )
        self.hydrate_row(plugin_menu)
        plugin_value = attr_element.get()
        host = self._find_host(self.host_menu.getValue())
        plugin = self._find_plugin(host, plugin_value)
        if not plugin:
            return
        plugin_menu.setValue(plugin["description"])

        plugin_menu.changeCommand(
            pm.Callback(self.on_plugin_menu_change, attr_element, plugin_menu)
        )

        return row

    def hydrate_row(self, plugin_menu):
        """
        Populates the plugin menu with available options based on the selected host.

        Args:
            plugin_menu: The optionMenu control to populate with plugin options.
        """
        pm.setParent(plugin_menu, menu=True)
        plugin_menu.clear()
        host = self._find_host(self.host_menu.getValue())

        if host["plugins"]:
            for item in host["plugins"]:
                pm.menuItem(label=item["description"])
            plugin_menu.setValue(host["plugins"][0]["description"])

    def hydrate(self, model):
        """
        Updates the UI elements of the control to reflect the provided model data.

        Args:
            model: The data model containing host and plugin information to display in the UI.
        """
        self.model = model
        pm.setParent(self.host_menu, menu=True)
        self.host_menu.clear()
        if not self.model:
            return

        for item in self.model:
            pm.menuItem(label=item["description"])
        # set menu to "none"
        self.host_menu.setValue(self.model[0]["description"])
        if self.is_unconnected_model():
            return

        host_attribute = self._get_host_attribute()
        if not host_attribute:
            return
        host = self._find_host(host_attribute.get())
        if not host:
            # delete the host and all the plugin entries
            self._clear_software(with_host=True)
            return

        # host exists, set the host menu to the host description
        self.host_menu.setValue(host["description"])

        for widget in (
            pm.columnLayout(self.plugins_column, q=True, childArray=True) or []
        ):
            pm.deleteUI(widget)
        # make sure all the plugin attributes are in the model
        for attr_element in self._get_plugin_attributes():
            plugin = self._find_plugin(host, attr_element.get())
            if plugin:
                self.create_row(attr_element)
            else:
                pm.removeMultiInstance(attr_element, b=True)

    def bind(self, attribute):
        """
        Associates the control with a Maya attribute.

        Args:
            attribute: The Maya attribute to bind to the control.
        """
        self.attribute = attribute
        self.host_menu.changeCommand(pm.Callback(self.on_host_menu_change))
        pm.button(self.add_btn, edit=True, command=pm.Callback(self.on_add_entry))
        self.hydrate(k.UNCONNECTED_MODEL)

    def on_host_menu_change(self):
        """
        Callback function that updates the attribute and UI when the selected host changes.
        """
        description = self.host_menu.getValue()
        name = self._find_host(description)["name"]
        self.attribute[0].set(name)
        self._clear_software()

    def on_plugin_menu_change(self, attribute, plugin_menu):
        """
        Callback function that updates the attribute when the selected plugin changes.

        Args:
            attribute: The attribute to update with the selected plugin's name.
            plugin_menu: The optionMenu control reflecting the plugin selection.
        """
        plugin_description = plugin_menu.getValue()
        host = self._find_host(self.host_menu.getValue())
        plugin = self._find_plugin(host, plugin_description)
        if not plugin:
            return
        attribute.set(plugin["name"])

    def _clear_software(self, with_host=False):
        """
        Clears the software stack control by removing all plugin entries and optionally the host entry.

        Args:
            with_host (bool): If True, also clears the host entry.
        """
        for widget in (
            pm.columnLayout(self.plugins_column, q=True, childArray=True) or []
        ):
            pm.deleteUI(widget)

        if with_host:
            self.host_menu.setValue(self.model[0]["description"])

        for i, attr_element in enumerate(self.attribute):
            if i == 0 and not with_host:
                continue
            pm.removeMultiInstance(attr_element, b=True)

        for widget in (
            pm.columnLayout(self.plugins_column, q=True, childArray=True) or []
        ):
            pm.deleteUI(widget)

    def _find_host(self, name_or_description):
        """
        Retrieves the host object from the model based on a given name or description.

        Args:
            name_or_description (str): The name or description of the host to find.

        Returns:
            The host object if found, otherwise None.
        """
        return next(
            (
                item
                for item in self.model
                if name_or_description in [item["name"], item["description"]]
            ),
            None,
        )

    def _find_plugin(self, host, name_or_description):
        """
        Retrieves the plugin object from the host based on a given name or description.

        Args:
            host (dict): The host dictionary containing plugin information.
            name_or_description (str): The name or description of the plugin to find.

        Returns:
            The plugin object if found, otherwise None.
        """
        if not (host and "plugins" in host):
            return None

        # Use 'next' with a generator expression to find the first matching item
        return next(
            (
                item
                for item in host["plugins"]
                if name_or_description in [item["name"], item["description"]]
            ),
            None,
        )

    def _get_plugin_attributes(self):
        """
        Retrieves a list of plugin attributes associated with the control, excluding the first (host) attribute.

        Returns:
            A list of plugin attributes.
        """
        if not len(list(self.attribute)):
            return []
        return [attr for attr in self.attribute if attr != self.attribute[0]]

    def _get_host_attribute(self):
        """
        Retrieves the first attribute associated with the control, typically representing the host.

        Returns:
            The host attribute, or None if no attributes are associated.
        """
        if not len(list(self.attribute)):
            return None
        return self.attribute[0]

    def is_unconnected_model(self):
        """
        Checks whether the current model is in a 'not connected' state, indicated by a specific placeholder description.

        Returns:
            True if the model is in the 'not connected' state, False otherwise.
        """
        return self.model[0]["description"] == k.UNCONNECTED_MODEL[0]["description"]


def _form_layout(*widgets, **kwargs):
    """
    Creates a form layout for a given set of widgets and applies standard spacing and attachments.

    Args:
        *widgets: Variable length widget list to include in the form layout.
        **kwargs: Additional keyword arguments (unused).

    Returns:
        The created form layout object.
    """
    form = pm.formLayout(nd=100)
    for widget in widgets:
        pm.control(widget, edit=True, parent=form)

    form.attachForm(widgets[0], "left", k.FORM_SPACING_X)
    form.attachControl(widgets[0], "right", k.FORM_SPACING_X, widgets[1])
    form.attachForm(widgets[0], "top", k.FORM_SPACING_Y)
    form.attachForm(widgets[0], "bottom", k.FORM_SPACING_Y)

    form.attachNone(widgets[1], "left")
    form.attachForm(widgets[1], "right", k.FORM_SPACING_X)
    form.attachForm(widgets[1], "top", k.FORM_SPACING_Y)
    form.attachForm(widgets[1], "bottom", k.FORM_SPACING_Y)

    return form
