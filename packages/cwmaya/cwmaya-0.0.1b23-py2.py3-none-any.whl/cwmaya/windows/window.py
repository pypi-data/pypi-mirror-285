import pymel.core.uitypes as gui
import pymel.core as pm
import time
from cwmaya.menus import tools_menu
import cwmaya.helpers.const as k
from cwmaya.helpers import conductor_helpers, workflow_api_helpers, desktop_app_helpers

from cwmaya.template.registry import TEMPLATES


class StormWindow(gui.Window):
    
    _instance = None
    
    def __init__(self):

        others = pm.lsUI(windows=True)
        for win in others:
            title = pm.window(win, q=True, title=True).split("|")[0].strip()
            if title == k.WINDOW_TITLE:
                pm.deleteUI(win)
        StormWindow._instance = self
        
        self.node = None
        self.setTitle(k.WINDOW_TITLE)
        self.setIconName(k.WINDOW_TITLE)
        self.setWidthHeight(k.WINDOW_DIMENSIONS)

        self.menuBarLayout = pm.menuBarLayout()
        self.tools_menu = tools_menu.create(self)

        self.form = pm.formLayout(nd=100)
        self.nameField = pm.nameField(width=200, height=30)
        self.tabLayout = pm.tabLayout(changeCommand=pm.Callback(self.on_tab_changed))

        pm.setParent(self.form)
        self.submit_but = pm.button(
            label="Submit",
            command=pm.Callback(self.submit),
        )

        self.composer_but = pm.button(
            label="Send to composer",
            command=pm.Callback(self.send_to_composer),
        )
        self.cancel_but = pm.button(label="Cancel", command=pm.Callback(self.on_cancel))
        self.layoutForm()

        pm.setParent(self.tabLayout)
        self.tabs = {}

        self.show()
        self.setResizeToFitChildren()

        self.load_with_first_preset()

    def setTitleAndName(self, node):
        name = node.name()
        title = f"Storm Tools | {name}"
        self.setTitle(title)
        self.setIconName(title)
        pm.nameField(self.nameField, edit=True, o=node)

    def layoutForm(self):

        self.form.attachForm(self.nameField, "top", 2)
        self.form.attachPosition(self.nameField, "left", 2, 50)
        self.form.attachForm(self.nameField, "right", 2)
        self.form.attachNone(self.nameField, "bottom")

        self.form.attachForm(self.tabLayout, "left", 2)
        self.form.attachForm(self.tabLayout, "right", 2)
        self.form.attachControl(self.tabLayout, "top", 2, self.nameField)
        self.form.attachControl(self.tabLayout, "bottom", 2, self.submit_but)

        self.form.attachNone(self.submit_but, "top")
        self.form.attachForm(self.submit_but, "right", 2)
        self.form.attachPosition(self.submit_but, "left", 2, 66)
        self.form.attachForm(self.submit_but, "bottom", 2)

        self.form.attachNone(self.composer_but, "top")
        self.form.attachControl(self.composer_but, "right", 2, self.submit_but)
        self.form.attachPosition(self.composer_but, "left", 2, 33)
        self.form.attachForm(self.composer_but, "bottom", 2)

        self.form.attachNone(self.cancel_but, "top")
        self.form.attachControl(self.cancel_but, "right", 2, self.composer_but)
        self.form.attachForm(self.cancel_but, "left", 2)
        self.form.attachForm(self.cancel_but, "bottom", 2)

    def clear_tabs(self):
        for tab in self.tabs.values():
            pm.deleteUI(tab)
        self.tabs = {}

    def on_cancel(self):
        print("on_cancel")

    def on_tab_changed(self):
        print("on_tab_changed")

    def load_with_first_preset(self):
        """
        Ensure that at least one node of a registered type exists. If not, create a default node.

        Args:
            dialog: The PyMel UI dialog where the node information will be displayed.
        """
        node_types = list(TEMPLATES.keys())
        nodes = pm.ls(type=node_types)
        if not nodes:
            self.create_template(node_types[0])
            return
        last_node = max(nodes, key=lambda n: n.attr("lastLoadedTemplate").get() or 0)
        self.load_template(last_node)

    def load_template(self, node):
        """
        Load a preset based on the node type and bind it to the dialog.

        Args:
            node: The node for which the preset is loaded.
            dialog: The PyMel UI dialog to update with the loaded preset.
        """
        self.node = node
        current_timestamp = int(time.time())
        self.node.attr("lastLoadedTemplate").set(current_timestamp)

        node_type = node.type()
        klass = TEMPLATES.get(node_type)
        if not klass:
            return

        klass.bind(node, self)

        pm.evalDeferred(
            pm.Callback(conductor_helpers.hydrate_coredata, self, force=False)
        )

    def create_template(self, node_type):
        """
        Create a new node of the specified type and load its preset into the dialog.

        Args:
            node_type: The type of node to be created.
            dialog: The PyMel UI dialog where the new node's preset will be applied.
        """

        klass = TEMPLATES.get(node_type)
        if not klass:
            return
        node = pm.createNode(node_type)
        klass.setup(node)
        self.load_template(node)

    def send_to_composer(self):
        """
        Send the current node to the composer.
        """
        desktop_app_helpers.send_to_composer(self.node)

    def submit(self):
        """
        Submit the current node to the workflow API.
        """
        workflow_api_helpers.submit(self.node)

    @classmethod
    def get_instance(cls):
        return cls._instance