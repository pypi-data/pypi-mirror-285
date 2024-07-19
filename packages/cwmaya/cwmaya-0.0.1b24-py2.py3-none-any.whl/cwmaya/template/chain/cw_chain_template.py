# -*- coding: utf-8 -*-

import pymel.core as pm

from cwmaya.tabs import general_tab, simple_tab, job_tab
from cwmaya.template.helpers import cw_template_base


class CwChainTemplate(cw_template_base.CwTemplateBase):

    CONNECTIONS = [
        ("defaultRenderGlobals.startFrame", "startFrame"),
        ("defaultRenderGlobals.endFrame", "endFrame"),
        ("defaultRenderGlobals.byFrameStep", "byFrame"),
        ("time1.outTime", "currentTime"),
    ]

    @classmethod
    def bind(cls, node, dialog):

        super().bind(node, dialog)

        pm.setParent(dialog.tabLayout)
        dialog.tabs["general_tab"] = general_tab.GeneralTab()

        pm.setParent(dialog.tabLayout)
        dialog.tabs["wrk_tab"] = simple_tab.SimpleTab()

        pm.setParent(dialog.tabLayout)
        dialog.tabs["job_tab"] = job_tab.JobTab()

        pm.setParent(dialog.tabLayout)

        dialog.tabLayout.setTabLabel((dialog.tabs["general_tab"], "Frames"))
        dialog.tabLayout.setTabLabel((dialog.tabs["wrk_tab"], "Work"))
        dialog.tabLayout.setTabLabel((dialog.tabs["job_tab"], "Job"))

        dialog.tabs["general_tab"].bind(node)
        dialog.tabs["wrk_tab"].bind(node, "wrk")
        dialog.tabs["job_tab"].bind(node)
        dialog.tabLayout.setSelectTabIndex(2)
