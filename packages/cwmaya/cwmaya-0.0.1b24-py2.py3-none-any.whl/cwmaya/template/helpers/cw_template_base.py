# -*- coding: utf-8 -*-

import pymel.core as pm

class CwTemplateBase(object):

    CONNECTIONS = []

    @classmethod
    def setup(cls, node):
        pm.nodePreset( load=(node, "default") )

        for src, dest in cls.CONNECTIONS:
            src = pm.Attribute(src)
            dest = node.attr(dest)
            if not pm.isConnected(src, dest):
                pm.displayInfo("connectAttr: {} {}".format(src, dest))
                src.connect(dest)

    @classmethod
    def bind(cls, node, dialog):
        dialog.setTitleAndName(node)
        dialog.clear_tabs()

