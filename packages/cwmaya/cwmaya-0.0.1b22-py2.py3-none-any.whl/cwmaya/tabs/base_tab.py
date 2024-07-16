import pymel.core as pm
import pymel.core.uitypes as gui
from cwmaya.widgets.dual_option_menu import DualOptionMenuControl
from cwmaya.widgets.kv_pairs import KvPairsControl
from cwmaya.widgets.asset_list import AssetListControl
from cwmaya.widgets.integer_field import IntFieldControl
from cwmaya.widgets.checkbox import CheckboxControl
from cwmaya.widgets.commands import CommandsControl
from cwmaya.widgets.script import ScriptControl
from cwmaya.widgets.text_field import TextFieldControl
from cwmaya.widgets.hidable_text_field import HidableTextFieldControl
from cwmaya.widgets.software_stack_control import SoftwareStackControl
from cwmaya.helpers import const as k


class BaseTab(gui.FormLayout):

    ATTRIBUTE_PREFIX = ""

    def __init__(self):
        """
        Create the UI.
        """
        self.setNumberOfDivisions(100)
        pm.setParent(self)
        self.scroll = pm.scrollLayout(childResizable=True)
        self.layout_scroll()
        pm.setParent(self.scroll)
        self.form = pm.formLayout()

        pm.setParent(self.form)

        self.column = pm.columnLayout()
        self.column.adjustableColumn(True)
        self.form.attachForm(self.column, "left", k.FORM_SPACING_X)
        self.form.attachForm(self.column, "right", k.FORM_SPACING_X)
        self.form.attachForm(self.column, "top", k.FORM_SPACING_Y)
        self.form.attachForm(self.column, "bottom", k.FORM_SPACING_Y)

        # Common task UI
        self.inst_type_ctl = None
        self.preemptible_ctl = None
        self.software_ctl = None
        self.commands_ctl = None
        self.extra_assets_ctl = None
        self.environment_ctl = None
        self.output_path_ctl = None

    def build_ui(self):
        raise NotImplementedError

    def layout_scroll(self):
        self.attachForm(self.scroll, "left", k.FORM_SPACING_X)
        self.attachForm(self.scroll, "right", k.FORM_SPACING_X)
        self.attachForm(self.scroll, "top", k.FORM_SPACING_Y)
        self.attachForm(self.scroll, "bottom", k.FORM_SPACING_Y)

    def bind(self, node):
        raise NotImplementedError

    def hydrate_coredata(self, **kwargs):
        pass

    @staticmethod
    def create_extra_assets_control(parent):
        pm.setParent(parent)
        pm.frameLayout(label="Extra assets")
        return AssetListControl()

    @staticmethod
    def create_kvpairs_control(parent, label):
        pm.setParent(parent)
        pm.frameLayout(label=label)
        return KvPairsControl()

    @staticmethod
    def create_inst_type_control(parent):
        pm.setParent(parent)
        pm.frameLayout(label="Hardware")
        col = pm.columnLayout()
        menu_ctl = DualOptionMenuControl()
        menu_ctl.set_label("Instance type")
        pm.setParent(col)
        checkbox_ctl = CheckboxControl()
        checkbox_ctl.set_label("Preemptible")
        pm.setParent(parent)
        return menu_ctl, checkbox_ctl

    @staticmethod
    def create_software_control(parent):
        pm.setParent(parent)
        pm.frameLayout(label="Software")
        result = SoftwareStackControl()
        return result

    @staticmethod
    def create_commands_control(parent):
        pm.setParent(parent)
        pm.frameLayout(label="Commands")
        return CommandsControl()

    @staticmethod
    def create_per_task_control(parent):
        pm.setParent(parent)
        result = IntFieldControl()
        result.set_label("Frames per task")
        return result

    @staticmethod
    def create_output_path_control(parent):
        pm.setParent(parent)
        pm.frameLayout(label="Outputs")
        result = TextFieldControl()
        result.set_label("Output path")
        return result

    @staticmethod
    def create_int_control(parent, label):
        pm.setParent(parent)
        result = IntFieldControl()
        result.set_label(label)
        return result

    @staticmethod
    def create_hidable_text_control(parent, label):
        pm.setParent(parent)
        result = HidableTextFieldControl()
        result.set_label(label)
        return result

    @staticmethod
    def create_text_control(parent, label):
        pm.setParent(parent)
        result = TextFieldControl()
        result.set_label(label)
        return result

    @staticmethod
    def create_script_control(parent, label):
        pm.setParent(parent)
        pm.frameLayout(label=label)
        return ScriptControl()
