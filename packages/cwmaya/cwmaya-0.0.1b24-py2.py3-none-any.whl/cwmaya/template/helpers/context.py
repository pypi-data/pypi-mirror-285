"""
Module to manage the context in which strings are interpolated.

Static context is the context that is the same for all frames in a sequence.
Dynamic context is the context that changes with each chunk.
"""

import os
import maya.cmds as cmds
import socket
import cwmaya.helpers.const as k


def getStatic(this_node, sequences=None):

    scenepath = cmds.file(q=True, sn=True)
    scenename = os.path.splitext(cmds.file(q=True, sn=True, shn=True))[0]
    scenedir = os.path.dirname(scenepath)
    mayaprojdir = cmds.workspace(q=True, rd=True).rstrip("/")
    imagesdir = cmds.workspace(expandName=cmds.workspace(fileRuleEntry="images"))
    stormdir = os.path.join(mayaprojdir, "storm")
    
    modeversion = cmds.moduleInfo(version=True, moduleName=k.MODULE_NAME)
    modfile = cmds.moduleInfo(definition=True, moduleName=k.MODULE_NAME)
    modpath = cmds.moduleInfo(path=True, moduleName=k.MODULE_NAME)
    packagedir = os.path.dirname(modpath)
    remotemodule = os.path.join(packagedir, "storm_remote")

    nodename = this_node.name()
    hostname = socket.getfqdn()
    username = os.getlogin()

    result = {
        "nodename": nodename,
        "scenepath": scenepath,
        "scenename": scenename,
        "scenedir": scenedir,
        "mayaprojdir": mayaprojdir,
        "imagesdir": imagesdir,
        "hostname": hostname,
        "username": username,
        "stormdir": stormdir,
        "modeversion": modeversion,
        "modfile": modfile,
        "modpath": modpath,
        "packagedir": packagedir,
        "remotemodule": remotemodule,
    }

    if sequences and sequences["main_sequence"]:
        result["sequence"] = str(sequences["main_sequence"])
        result["seqstart"] = str(sequences["main_sequence"].start)
        result["seqend"] = str(sequences["main_sequence"].end)
        result["seqlen"] = str(len(sequences["main_sequence"]))

    return result


def getDynamic(static_context, chunk):
    context = static_context.copy()
    context["chunk"] = str(chunk)
    context["start"] = str(chunk.start)
    context["end"] = str(chunk.end)
    context["step"] = str(chunk.step)
    context["chunklen"] = str(len(chunk))
    return context


def interpolate(string, context, fail_on_error=True):
    """
    Interpolates a string with a given context using format.

    Parameters:
    - string (str): The string to be interpolated.
    - context (dict): The dictionary containing the context for interpolation.
    - fail_on_error (bool): If true, raises an error with details on failure.

    Returns:
    - str: The interpolated string.

    Raises:
    - KeyError: If fail_on_error is True and interpolation fails due to missing keys.
    - ValueError: If fail_on_error is False and interpolation fails due to missing keys.
    """
    try:
        return string.format(**context)
    except KeyError as ex:
        if fail_on_error:
            missing_key = ex.args[0]
            valid_keys = ", ".join(context.keys())
            raise KeyError(
                f"Missing key '{missing_key}' in context. Valid keys are: {valid_keys}"
            ) from ex
        else:
            cmds.warning(
                f"Failed to interpolate string '{string}' with context '{context}'. Missing key: {ex.args[0]}"
            )
            # If fail_on_error is False, return the original string with placeholders intact
            return string
