
# -*- coding: utf-8 -*-

import pymel.core as pm
import os
import cwmaya.helpers.const as k
import shutil

def save_preset(node, preset=None):
    """
    Save the current state of the node as a preset.
    """
    if not preset:
        preset = prompt_for_preset_name()
    if not preset:
        return

    pm.nodePreset( save=(node, preset) )

    print(f"Saved preset: {preset} for node: {node}")

def load_preset(node, preset, dialog=None):
    """
    Load the specified preset onto the node.
    """
    print(f"Loading preset: {preset} onto node: {node}")
    pm.nodePreset( load=(node, preset) )
    if dialog:
        dialog.load_template(node)

def prompt_for_preset_name():
    """
    Prompt the user for a preset name.
    """
    result = pm.promptDialog(
        title='Save Preset',
        message='Enter Name:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel')

    if not (result == 'OK'):
        return None
    
    preset = pm.promptDialog(query=True, text=True)
    if not pm.nodePreset(isValidName=preset):
        pm.error("Invalid preset name")
        return None
    return preset

def install_presets(force=False):
    """
    Install the presets that the developer has set up and included in the distribution.
    
    Should include a default preset for each node type, so that the new nodes are hydrated on creation.
    
    Only presets if that don't already exist in the user's presets folder.
    """
    
    mod_path = pm.moduleInfo(path=True, moduleName=k.MODULE_NAME)
    mod_presets_folder = os.path.join(mod_path, "presets")
    presets_folder = pm.internalVar(userPresetsDir=True)
    # copy contents from mod_presets_folder to presets_folder unless they already exist
    for file in os.listdir(mod_presets_folder):
        fn = os.path.join(mod_presets_folder, file)
        if not os.path.isfile(fn):
            continue
        if force or not os.path.exists(os.path.join(presets_folder, file)):
            shutil.copy(os.path.join(mod_presets_folder, file), presets_folder)
            print(f"Installed preset: {file}")
        else:
            if not pm.about(batch=True):
                print(f"Preset already exists: {file}. If you want to force install factory presets, open Storm Tools and go to Tools->Force install factory presets.")
            
def copy_presets_to_module(destination=None):
    """
    Copy the presets from the user's presets folder to the module's presets folder.
    
    This is not exposed to users, and is for the benefit of developers who want to copy their presets to the module for distribution.
    """
    
    mod_path = pm.moduleInfo(path=True, moduleName=k.MODULE_NAME)
    if not destination:
        mod_presets_folder = os.path.join(mod_path, "presets")
    else:
        mod_presets_folder = destination
    presets_folder = pm.internalVar(userPresetsDir=True)
    for file in os.listdir(presets_folder):
        # only copy if its a file
        fn = os.path.join(presets_folder, file)
        if os.path.isfile(fn):
            shutil.copy(fn, mod_presets_folder)
            print(f"Copied preset: {file}")
