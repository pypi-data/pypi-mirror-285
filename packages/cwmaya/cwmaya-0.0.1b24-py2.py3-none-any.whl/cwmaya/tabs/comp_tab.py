import pymel.core as pm
from cwmaya.tabs.base_tab import BaseTab
import cwmaya.helpers.const as k


class CompTab(BaseTab):

    def build_ui(self):
        """
        Create the frame that contains the export options.
        """
        pm.setParent(self.column)
        frame = pm.frameLayout(label="General")

        self.per_task_ctl = self.create_per_task_control(frame)
        
        menu, checkbox = self.create_inst_type_control(frame)
        self.inst_type_ctl = menu
        self.preemptible_ctl = checkbox
        
        self.software_ctl = self.create_software_control(self.column)

        self.commands_ctl = self.create_commands_control(self.column)

        self.extra_assets_ctl = self.create_extra_assets_control(self.column)
        self.environment_ctl = self.create_kvpairs_control(self.column, "Environment")
        self.output_path_ctl = self.create_output_path_control(self.column)

        return frame

    def bind(self, node):
        """Bind this UI to the given node."""
        self.per_task_ctl.bind(node.attr("cmpPerTask"))
        self.inst_type_ctl.bind(node.attr("cmpInstanceType"))
        self.preemptible_ctl.bind(node.attr("cmpPreemptible"))
        self.software_ctl.bind(node.attr("cmpSoftware"))
        self.environment_ctl.bind(node.attr("cmpEnvironment"))
        self.extra_assets_ctl.bind(node.attr("cmpExtraAssets"))
        self.commands_ctl.bind(node.attr("cmpCommands"))
        self.output_path_ctl.bind(node.attr("cmpOutputPath"))
        return

