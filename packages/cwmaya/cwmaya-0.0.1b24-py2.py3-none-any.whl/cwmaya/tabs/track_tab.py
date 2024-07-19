import pymel.core as pm
from cwmaya.tabs.base_tab import BaseTab


class TrackTab(BaseTab):


    def build_ui(self):
        """
        Create the frame that contains the export options.
        """
        pm.setParent(self.column)
        frame = pm.frameLayout(label="General")

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
        self.inst_type_ctl.bind(node.attr("trkInstanceType"))
        self.preemptible_ctl.bind(node.attr("trkPreemptible"))
        self.software_ctl.bind(node.attr("trkSoftware"))
        self.environment_ctl.bind(node.attr("trkEnvironment"))
        self.extra_assets_ctl.bind(node.attr("trkExtraAssets"))
        self.commands_ctl.bind(node.attr("trkCommands"))
        self.output_path_ctl.bind(node.attr("trkOutputPath"))
        return
