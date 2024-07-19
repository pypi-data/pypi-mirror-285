import os
import maya.cmds as cmds

import cwmaya.helpers.const as k


def scrape():
    """Scrape assets from the current scene."""
    # Get all the assets in the scene
    assets = []
    scenepath = cmds.file(q=True, sn=True)
    assets.append(scenepath)
    references = cmds.file(q=True, r=True)
    for ref in references:
        refpath = cmds.referenceQuery(ref, f=True)
        assets.append(refpath)

    modpath = cmds.moduleInfo(path=True, moduleName=k.MODULE_NAME)
    packagedir = os.path.dirname(modpath)
    remotemodule = os.path.join(packagedir, "storm_remote")
    assets.append(remotemodule)
    
    ws = cmds.workspace(q=True, rd=True)
    wsmel = os.path.join(ws, "workspace.mel") 
    assets.append(wsmel)

    return assets
