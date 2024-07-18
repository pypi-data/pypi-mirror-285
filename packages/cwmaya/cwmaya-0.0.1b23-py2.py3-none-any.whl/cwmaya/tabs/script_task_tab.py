from cwmaya.tabs.task_tab import TaskTab


class ScriptTaskTab(TaskTab):

    def __init__(self):

        super(ScriptTaskTab, self).__init__()

        self.script_ctl = None

        self.build_ui()

    def build_ui(self):
        self.label_ctl = self.create_text_control(self.column, "Label")
        menu, checkbox = self.create_inst_type_control(self.column)
        self.inst_type_ctl = menu
        self.preemptible_ctl = checkbox
        self.software_ctl = self.create_software_control(self.column)

        self.script_ctl = self.create_script_control(self.column, "Maya batch script")

        self.commands_ctl = self.create_commands_control(self.column)
        self.extra_assets_ctl = self.create_extra_assets_control(self.column)
        self.environment_ctl = self.create_kvpairs_control(self.column, "Environment")
        self.output_path_ctl = self.create_output_path_control(self.column)

    def enable_commands(self, use_script):
        self.commands_ctl.setEnable(not use_script)

    def bind(self, node, prefix):
        super(ScriptTaskTab, self).bind(node, prefix)
        self.script_ctl.bind(node, prefix, use_script_changed=self.enable_commands)
