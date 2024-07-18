import sys
import os
import maya.api.OpenMaya as om
import maya.cmds as cmds


CIODIR = os.environ.get("CWMAYA_CIODIR")
sys.path.append(CIODIR)

from cwmaya.template.helpers.cw_submission_base import cwSubmission
from cwmaya.template.smoke.cw_smoke_submission import cwSmokeSubmission
from cwmaya.template.sim_render.cw_sim_render_submission import cwSimRenderSubmission
from cwmaya.template.chain.cw_chain_submission import cwChainSubmission
from cwmaya.menus import coreweave_menu
from cwmaya.helpers import preset_helpers


def maya_useNewAPI():
    pass


def initializePlugin(obj):

    plugin = om.MFnPlugin(obj, "CoreWeave", "0.0.1-beta.23", "Any")

    try:
        plugin.registerNode(
            "cwSubmission",
            cwSubmission.id,
            cwSubmission.creator,
            cwSubmission.initialize,
            om.MPxNode.kDependNode,
        )

        plugin.registerNode(
            "cwSmokeSubmission",
            cwSmokeSubmission.id,
            cwSmokeSubmission.creator,
            cwSmokeSubmission.initialize,
            om.MPxNode.kDependNode,
        )

        plugin.registerNode(
            "cwSimRenderSubmission",
            cwSimRenderSubmission.id,
            cwSimRenderSubmission.creator,
            cwSimRenderSubmission.initialize,
            om.MPxNode.kDependNode,
        )

        plugin.registerNode(
            "cwChainSubmission",
            cwChainSubmission.id,
            cwChainSubmission.creator,
            cwChainSubmission.initialize,
            om.MPxNode.kDependNode,
        )

        create_storm_shelf()
        create_file_rules()
        install_presets()

    except:
        sys.stderr.write("Failed to register submission nodes\n")
        raise

    coreweave_menu.load()


def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)

    try:
        remove_storm_shelf()
        plugin.deregisterNode(cwChainSubmission.id)
        plugin.deregisterNode(cwSimRenderSubmission.id)
        plugin.deregisterNode(cwSmokeSubmission.id)
        plugin.deregisterNode(cwSubmission.id)
    except:
        sys.stderr.write("Failed to deregister submission nodes\n")
        raise

    coreweave_menu.unload()


# We'll move this shelf stuff to its own module.
def create_storm_shelf():
    shelf_name = "Storm"

    # Delete the shelf if it already exists
    if cmds.shelfLayout(shelf_name, exists=True):
        cmds.deleteUI(shelf_name, layout=True)

    # Create a new shelf
    cmds.shelfLayout(shelf_name, parent="ShelfLayout")

    # Add buttons to the shelf
    cmds.shelfButton(
        label="My Button",
        command='print("Button Pressed")',
        image1="commandButton.png",  # Path to your icon file
        parent=shelf_name,
    )

    cmds.shelfButton(
        label="Storm Window",
        command="from cwmaya.menus.coreweave_menu import show_storm_window;show_storm_window()",
        image1="commandButton.png",  
        parent=shelf_name,
    )

    cmds.shelfButton(
        label="Desktop Health",
        command="from cwmaya.helpers import desktop_app_helpers;desktop_app_helpers.health_check()",
        image1="da_health_128x128.png",
        parent=shelf_name,
    )

    cmds.shelfButton(
        label="Workflow API Health",
        command="from cwmaya.helpers import workflow_api_helpers;workflow_api_helpers.health_check()",
        image1="wf_health_128x128.png",
        parent=shelf_name,
    )


    cmds.shelfButton(
        label="Select current template",
        command="from cwmaya.helpers import spec_helpers;from cwmaya.windows import window;win = spec_helpers.select_current_template(window.StormWindow.get_instance())",
        image1="tp_select_128x128.png",
        parent=shelf_name,
    )


def remove_storm_shelf():
    shelf_name = "Storm"
    if cmds.shelfLayout(shelf_name, exists=True):
        cmds.deleteUI(shelf_name, layout=True)


def create_file_rules():
    cmds.workspace(fileRule=["storm", "storm/"])
    cmds.workspace(fileRule=["storm_cache", "storm/cache"])
    cmds.workspace(fileRule=["storm_scenes", "storm/scenes"])
    cmds.workspace(fileRule=["storm_comp", "storm/comp"])


def install_presets():
    """
    Install the presets that the developer has set up and included in the distribution.

    Should include a default preset for each node type, so that the new nodes are hydrated on creation.

    Only presets if that don't already exist in the user's presets folder.
    """
    preset_helpers.install_presets()
