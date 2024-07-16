# -*- coding: utf-8 -*-

import pymel.core as pm

from cwmaya.tabs import simple_tab, job_tab
from cwmaya.template.helpers import cw_template_base

class CwSmokeTemplate(cw_template_base.CwTemplateBase):

    @classmethod
    def bind(cls, node, dialog):

        super().bind(node, dialog)

        pm.setParent(dialog.tabLayout)
        dialog.tabs["work_tab"] = simple_tab.SimpleTab()

        pm.setParent(dialog.tabLayout)
        dialog.tabs["job_tab"] = job_tab.JobTab()

        pm.setParent(dialog.tabLayout)

        dialog.tabLayout.setTabLabel((dialog.tabs["work_tab"], "Work"))
        dialog.tabLayout.setTabLabel((dialog.tabs["job_tab"], "Job"))

        dialog.tabs["work_tab"].bind(node, "wrk")
        dialog.tabs["job_tab"].bind(node)

        dialog.tabLayout.setSelectTabIndex(1)
