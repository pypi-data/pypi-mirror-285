import pymel.core as pm
from cwmaya.tabs.base_tab import BaseTab
from cwmaya.widgets.hidable_text_field import HidableTextFieldControl
import cwmaya.helpers.const as k


class RenderTab(BaseTab):


    def build_ui(self):
        """
        Create the frame that contains the export options.
        """
        pm.setParent(self.column)
        frame = pm.frameLayout(label="General")

        self.custom_range_ctl = self.create_custom_range_ctl(frame)
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

    def create_custom_range_ctl(self, parent):
        pm.setParent(parent)
        result = HidableTextFieldControl()
        result.set_label("Use custom range")
        return result

    def bind(self, node):
        """Bind this UI to the given node."""
        self.custom_range_ctl.bind(
            node.attr("renUseCustomRange"), node.attr("renCustomRange")
        )
        self.per_task_ctl.bind(node.attr("renPerTask"))
        self.inst_type_ctl.bind(node.attr("renInstanceType"))
        self.preemptible_ctl.bind(node.attr("renPreemptible"))
        self.software_ctl.bind(node.attr("renSoftware"))
        self.environment_ctl.bind(node.attr("renEnvironment"))
        self.extra_assets_ctl.bind(node.attr("renExtraAssets"))
        self.commands_ctl.bind(node.attr("renCommands"))
        self.output_path_ctl.bind(node.attr("renOutputPath"))
        return
