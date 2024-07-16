# -*- coding: utf-8 -*-

import pymel.core as pm

from cwmaya.tabs import general_tab, simple_tab, script_task_tab, job_tab
from cwmaya.template.helpers import cw_template_base


class CwSimRenderTemplate(cw_template_base.CwTemplateBase):

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
        dialog.tabs["sim_tab"] = script_task_tab.ScriptTaskTab()

        pm.setParent(dialog.tabLayout)
        dialog.tabs["render_tab"] = simple_tab.SimpleTab()

        pm.setParent(dialog.tabLayout)
        dialog.tabs["quicktime_tab"] = simple_tab.SimpleTab()

        pm.setParent(dialog.tabLayout)
        dialog.tabs["job_tab"] = job_tab.JobTab()

        pm.setParent(dialog.tabLayout)

        dialog.tabLayout.setTabLabel((dialog.tabs["general_tab"], "Frames"))
        dialog.tabLayout.setTabLabel((dialog.tabs["sim_tab"], "Sim"))
        dialog.tabLayout.setTabLabel((dialog.tabs["render_tab"], "Render"))
        dialog.tabLayout.setTabLabel((dialog.tabs["quicktime_tab"], "Quicktime"))
        dialog.tabLayout.setTabLabel((dialog.tabs["job_tab"], "Job"))

        dialog.tabs["general_tab"].bind(node)
        dialog.tabs["sim_tab"].bind(node, "sim")
        dialog.tabs["render_tab"].bind(node, "rnd")
        dialog.tabs["quicktime_tab"].bind(node, "qtm")
        dialog.tabs["job_tab"].bind(node)
        dialog.tabLayout.setSelectTabIndex(2)
