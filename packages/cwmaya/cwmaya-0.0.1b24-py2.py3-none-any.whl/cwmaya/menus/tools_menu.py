import pymel.core as pm
from cwmaya.helpers import const as k
from cwmaya.helpers import (
    desktop_app_helpers,
    conductor_helpers,
    workflow_api_helpers,
    preset_helpers,
    spec_helpers,
)

from cwmaya.template.registry import TEMPLATES


def create(dialog):
    """
    Factory function to create a new instance of ToolsMenuGroup attached to the given dialog.

    Args:
        dialog: The PyMel UI dialog to which the menu group will be attached.
    """
    return ToolsMenuGroup(dialog)


class ToolsMenuGroup(object):

    def __init__(self, dialog):
        """
        Initialize the ToolsMenuGroup with a dialog and set up the initial
        menu structure.

        Args:
            dialog: The PyMel UI dialog to which this menu will be attached.
        """
        self.dialog = dialog
        pm.setParent(dialog.menuBarLayout)

        self.tools_menu = pm.menu(label="Tools", tearOff=True)

        self.create_general_section()
        self.create_templates_section()
        self.create_desktop_app_section()
        self.create_workflow_api_section()
        self.create_spec_section()
        self.create_presets_section()

    def create_general_section(self):
        pm.setParent(self.tools_menu, menu=True)
        pm.menuItem(divider=True, dividerLabel="General")
        pm.menuItem(
            label="Connect to Conductor",
            command=pm.Callback(
                conductor_helpers.hydrate_coredata, self.dialog, force=True
            ),
        )
        pm.menuItem(
            label="Show Account",
            command=pm.Callback(conductor_helpers.show_account),
        )

    def create_templates_section(self):
        pm.setParent(self.tools_menu, menu=True)
        pm.menuItem(divider=True, dividerLabel="Templates")

        ############### Load Template
        pm.setParent(self.tools_menu, menu=True)
        self.load_templates_menu = pm.menuItem(
            label="Load Template",
            subMenu=True,
            pmc=pm.Callback(self.post_load_template_cmd),
        )

        ############### Create Template
        pm.setParent(self.tools_menu, menu=True)
        self.create_templates_menu = pm.menuItem(
            label="Create Template",
            subMenu=True,
            pmc=pm.Callback(self.post_create_template_cmd),
        )

        ############### Select Current
        pm.setParent(self.tools_menu, menu=True)
        self.select_current_template_menu = pm.menuItem(
            label="Select current template",
            command=pm.Callback(spec_helpers.select_current_template, self.dialog),
        )

        ############### Duplicate Current
        self.duplicate_current_template_menu = pm.menuItem(
            label="Duplicate current template",
            command=pm.Callback(spec_helpers.duplicate_current_template, self.dialog),
        )

    def create_desktop_app_section(self):

        pm.setParent(self.tools_menu, menu=True)
        pm.menuItem(divider=True, dividerLabel="Desktop app")
        pm.menuItem(
            label="Health check", command=pm.Callback(desktop_app_helpers.health_check)
        )
        pm.menuItem(
            label="Open app", command=pm.Callback(desktop_app_helpers.open_app)
        )
        pm.menuItem(label="Navigate", subMenu=True)
        for route in k.DESKTOP_APP_ROUTES:
            pm.menuItem(
                label=route, command=pm.Callback(desktop_app_helpers.navigate, route)
            )
        pm.setParent(self.tools_menu, menu=True)
        pm.menuItem(
            label="Sync coredata",
            command=pm.Callback(self.on_send_coredata),
        )

    def create_workflow_api_section(self):
        pm.setParent(self.tools_menu, menu=True)
        pm.menuItem(divider=True, dividerLabel="Workflow API")

        pm.menuItem(
            label="Health check", command=pm.Callback(workflow_api_helpers.health_check)
        )
        pm.menuItem(
            label="List jobs", command=pm.Callback(workflow_api_helpers.list_jobs)
        )
        pm.menuItem(
            label="Validate job",
            command=pm.Callback(self.validate_job),
        )

    def create_spec_section(self):
        pm.setParent(self.tools_menu, menu=True)
        pm.menuItem(divider=True, dividerLabel="Spec")

        pm.menuItem(
            label="Show spec",
            command=pm.Callback(self.show_spec),
        )
        pm.menuItem(
            label="Show spec tokens",
            command=pm.Callback(self.show_tokens),
        )
        pm.menuItem(
            label="Export spec",
            command=pm.Callback(self.export_spec),
        )

        pm.menuItem(
            label="Export submission",
            command=pm.Callback(self.export_submission),
        )

    def create_presets_section(self):
        pm.setParent(self.tools_menu, menu=True)
        pm.menuItem(divider=True, dividerLabel="Presets")

        self.load_preset_menu = pm.menuItem(
            label="Load preset",
            subMenu=True,
            pmc=pm.Callback(self.post_load_preset_cmd),
        )

        pm.setParent(self.tools_menu, menu=True)
        self.save_preset_menu = pm.menuItem(
            label="Save preset",
            subMenu=True,
            pmc=pm.Callback(self.post_save_preset_cmd),
        )

        pm.setParent(self.tools_menu, menu=True)
        self.delete_preset_menu = pm.menuItem(
            label="Delete preset",
            subMenu=True,
            pmc=pm.Callback(self.post_delete_preset_cmd),
        )

        pm.setParent(self.tools_menu, menu=True)
        self.save_preset_as_default_menu = pm.menuItem(
            label="Save preset as default",
            command=pm.Callback(self.on_save_preset, preset="default"),
        )

        pm.setParent(self.tools_menu, menu=True)
        self.install_presets_menu = pm.menuItem(
            label="Force install factory presets",
            command=pm.Callback(self.on_force_install_presets),
        )

    def post_save_preset_cmd(self):
        pm.setParent(self.save_preset_menu, menu=True)
        pm.menu(self.save_preset_menu, edit=True, deleteAllItems=True)
        node = self.dialog.node
        valid_presets = pm.nodePreset(list=node)
        for preset in valid_presets:
            pm.menuItem(label=preset, command=pm.Callback(self.on_save_preset, preset))
        pm.menuItem(divider=True)
        pm.menuItem(label="New preset", command=pm.Callback(self.on_save_preset))

    def post_load_preset_cmd(self):
        pm.setParent(self.load_preset_menu, menu=True)
        pm.menu(self.load_preset_menu, edit=True, deleteAllItems=True)
        node = self.dialog.node
        valid_presets = pm.nodePreset(list=node)
        for preset in valid_presets:
            pm.menuItem(label=preset, command=pm.Callback(self.on_load_preset, preset))
        pm.setParent(self.load_preset_menu, menu=True)

    def post_delete_preset_cmd(self):
        pm.setParent(self.delete_preset_menu, menu=True)
        pm.menu(self.delete_preset_menu, edit=True, deleteAllItems=True)
        node = self.dialog.node
        valid_presets = pm.nodePreset(list=node)
        for preset in valid_presets:
            pm.menuItem(
                label=preset, command=pm.Callback(self.on_delete_preset, preset)
            )
        pm.setParent(self.delete_preset_menu, menu=True)

    # Dynamically build the Select and Create submenus just before the menu is opened,
    def post_load_template_cmd(self):
        """
        Dynamically build the Select and Create submenus just before the menu is opened,
        populating them based on existing nodes of registered types.
        """
        pm.setParent(self.load_templates_menu, menu=True)
        pm.menu(self.load_templates_menu, edit=True, deleteAllItems=True)
        for j in pm.ls(type=TEMPLATES.keys()):
            pm.menuItem(
                label=f"Load {str(j)}",
                command=pm.Callback(self.dialog.load_template, j),
            )

        pm.setParent(self.tools_menu, menu=True)

    def post_create_template_cmd(self):
        """
        Dynamically build the Select and Create submenus just before the menu is opened,
        populating them based on existing nodes of registered types.
        """
        pm.setParent(self.create_templates_menu, menu=True)

        pm.menu(self.create_templates_menu, edit=True, deleteAllItems=True)

        for j in TEMPLATES.keys():
            pm.menuItem(
                label=f"Create {str(j)}",
                command=pm.Callback(self.dialog.create_template, j),
            )
        pm.setParent(self.tools_menu, menu=True)

    def show_tokens(self):
        spec_helpers.show_tokens(self.dialog.node)

    def show_spec(self):
        spec_helpers.show_spec(self.dialog.node)

    def export_spec(self):
        spec_helpers.export_spec(self.dialog.node)

    def export_submission(self):
        workflow_api_helpers.export_submission(self.dialog.node)

    def validate_job(self):
        workflow_api_helpers.validate_job(self.dialog.node)

    def on_save_preset(self, preset=None):
        preset_helpers.save_preset(self.dialog.node, preset)

    def on_load_preset(self, preset):
        preset_helpers.load_preset(self.dialog.node, preset, dialog=self.dialog)

    def on_delete_preset(self, preset):
        pm.nodePreset(delete=(self.dialog.node, preset))

    def on_force_install_presets(self):
        preset_helpers.install_presets(force=True)

    def on_send_coredata(self):
        response = desktop_app_helpers.send_coredata()
        if response.ok:
            desktop_app_helpers.navigate("projects")
        else:
            pm.error(f"Error syncing coredata: {response.text}")
        