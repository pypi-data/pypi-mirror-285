# -*- coding: utf-8 -*-

import pymel.core as pm

from cwmaya.tabs import (
    export_tab,
    render_tab,
    comp_tab,
    quicktime_tab,
    track_tab,
    slack_tab,
    job_tab,
)


def bind(node, dialog):

    dialog.clear_tabs()

    pm.setParent(dialog.tabLayout)
    dialog.tabs["export_tab"] = export_tab.ExportTab()
    pm.setParent(dialog.tabLayout)
    dialog.tabs["render_tab"] = render_tab.RenderTab()
    pm.setParent(dialog.tabLayout)
    dialog.tabs["comp_tab"] = comp_tab.CompTab()
    pm.setParent(dialog.tabLayout)
    dialog.tabs["quicktime_tab"] = quicktime_tab.QuicktimeTab()
    pm.setParent(dialog.tabLayout)
    dialog.tabs["slack_tab"] = slack_tab.SlackTab()
    pm.setParent(dialog.tabLayout)
    dialog.tabs["track_tab"] = track_tab.TrackTab()
    pm.setParent(dialog.tabLayout)
    dialog.tabs["job_tab"] = job_tab.JobTab()
    pm.setParent(dialog.tabLayout)

    dialog.tabLayout.setTabLabel((dialog.tabs["export_tab"], "Export tasks"))
    dialog.tabLayout.setTabLabel((dialog.tabs["render_tab"], "Render tasks"))
    dialog.tabLayout.setTabLabel((dialog.tabs["comp_tab"], "Comp tasks"))
    dialog.tabLayout.setTabLabel((dialog.tabs["quicktime_tab"], "Quicktime task"))
    dialog.tabLayout.setTabLabel((dialog.tabs["track_tab"], "Track task"))
    dialog.tabLayout.setTabLabel((dialog.tabs["slack_tab"], "Slack task"))
    dialog.tabLayout.setTabLabel((dialog.tabs["job_tab"], "Job"))

    for tab in dialog.tabs.values():
        tab.bind(node)
    dialog.tabLayout.setSelectTabIndex(3)
 