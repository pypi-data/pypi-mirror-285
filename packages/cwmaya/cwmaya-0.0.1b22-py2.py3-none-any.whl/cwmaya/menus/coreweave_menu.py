# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pymel.core as pm


import webbrowser
import importlib


from cwmaya.windows import about_window, window
from cwmaya.helpers import reloader


MAYA_PARENT_WINDOW = "MayaWindow"
COREWEAVE_MENU = "CoreWeaveMenu"
CONDUCTOR_DOCS = "https://docs.conductortech.com/"
COREWEAVE_SUBMISSION_NODE = "cwSubmission"


def unload():

    if pm.menu(COREWEAVE_MENU, q=True, exists=True):
        pm.menu(COREWEAVE_MENU, e=True, deleteAllItems=True)
        pm.deleteUI(COREWEAVE_MENU)


def load():
    unload()
    CoreWeaveMenu()


class CoreWeaveMenu(object):
    def __init__(self):

        if not pm.about(batch=True):
            pm.setParent(MAYA_PARENT_WINDOW)

            self.menu = pm.menu(COREWEAVE_MENU, label="CoreWeave", tearOff=True)

            pm.menuItem(label="Storm Window", command=pm.Callback(show_storm_window))

            pm.menuItem(divider=True)

            pm.setParent(self.menu, menu=True)

            pm.menuItem(divider=True)

            self.help_menu = pm.menuItem(
                label="Help",
                command=pm.Callback(webbrowser.open, CONDUCTOR_DOCS, new=2),
            )
            self.about_menu = pm.menuItem(
                label="About", command=pm.Callback(about_window.show)
            )


def show_storm_window():
    importlib.reload(reloader)
    importlib.reload(window)
    window.StormWindow()
