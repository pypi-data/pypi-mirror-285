# -*- coding: utf-8 -*-

from cwmaya.menus import tools_menu


from cwmaya.helpers import (
    const,
    layer_utils,
    node_utils,
    spec_helpers,
    preset_helpers,
    desktop_app_helpers,
    conductor_helpers,
    workflow_api_helpers,
)

from cwmaya.template.sim_render import cw_sim_render_template
from cwmaya.template.smoke import cw_smoke_template
from cwmaya.template.chain import cw_chain_template
from cwmaya.windows import about_window, window_utils, jobs_index

from cwmaya.tabs import (
    base_tab,
    comp_tab,
    export_tab,
    general_tab,
    job_tab,
    quicktime_tab,
    render_tab,
    simple_tab,
    script_task_tab,
    slack_tab,
    task_tab,
)

from cwmaya.widgets import (
    asset_list,
    checkbox,
    commands,
    script,
    dual_option_menu,
    hidable_text_field,
    integer_field,
    kv_pairs,
    single_option_menu,
    software_stack_control,
    text_area,
    text_field,
)

from cwstorm.dsl import cmd, dag_node, job, node_metaclass, node, task, upload


import importlib


importlib.reload(node_metaclass)
importlib.reload(node)
importlib.reload(dag_node)
importlib.reload(cmd)
importlib.reload(job)
importlib.reload(task)
importlib.reload(upload)

importlib.reload(const)

importlib.reload(hidable_text_field)
importlib.reload(text_field)
importlib.reload(integer_field)
importlib.reload(checkbox)

importlib.reload(text_area)
importlib.reload(kv_pairs)
importlib.reload(commands)
importlib.reload(script)
importlib.reload(dual_option_menu)
importlib.reload(single_option_menu)
importlib.reload(software_stack_control)
importlib.reload(asset_list)

# Tabs
importlib.reload(base_tab)
importlib.reload(task_tab)
importlib.reload(simple_tab)
importlib.reload(script_task_tab)
importlib.reload(job_tab)
importlib.reload(general_tab)
importlib.reload(export_tab)
importlib.reload(render_tab)
importlib.reload(quicktime_tab)
importlib.reload(comp_tab)
importlib.reload(slack_tab)

# Template
importlib.reload(preset_helpers)
importlib.reload(conductor_helpers)
importlib.reload(desktop_app_helpers)
importlib.reload(workflow_api_helpers)
importlib.reload(spec_helpers)
importlib.reload(cw_smoke_template)
importlib.reload(cw_sim_render_template)
importlib.reload(cw_chain_template)

# Windows
importlib.reload(about_window)
importlib.reload(jobs_index)


# Utils
importlib.reload(node_utils)
importlib.reload(layer_utils)
importlib.reload(window_utils)

# Menus
importlib.reload(tools_menu)
