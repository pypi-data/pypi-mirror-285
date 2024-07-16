import pymel.core.uitypes as gui
import pymel.core as pm
import cwmaya.helpers.const as k

DIALOG_MODE_FILES=4
DIALOG_MODE_FOLDER=3
class AssetListControl(gui.FormLayout):

    def __init__(self):
        """
        Create the UI.
        """
        super(AssetListControl, self).__init__()
        self.header_row = None
        self.column = None
        self.add_btn = None
        self.create_controls()

    def create_controls(self):

        pm.setParent(self)

        label = pm.text(label="", width=k.LABEL_WIDTH)

        form = pm.formLayout(nd=100, height=200)
        self.clear_all_btn = pm.button(label="Clear All", height=24)
        self.clear_sel_btn = pm.button(label="Remove Selection", height=24)
        self.browse_file_btn = pm.button(label="Browse Files", height=24)
        self.browse_dir_btn = pm.button(label="Browse Folder", height=24)
        self.scroll_list = pm.textScrollList(numberOfRows=10, allowMultiSelection=True)

        self.attachForm(label, "left", k.FORM_SPACING_X)
        self.attachNone(label, "right")
        self.attachForm(label, "top", k.FORM_SPACING_Y)
        self.attachForm(label, "bottom", k.FORM_SPACING_Y)

        self.attachControl(form, "left", k.FORM_SPACING_X, label)
        self.attachForm(form, "right", k.FORM_SPACING_X)
        self.attachForm(form, "top", k.FORM_SPACING_Y)
        self.attachForm(form, "bottom", k.FORM_SPACING_Y)

        form.attachForm(self.clear_all_btn, "left", k.FORM_SPACING_X)
        form.attachPosition(self.clear_all_btn, "right", k.FORM_SPACING_X, 25)
        form.attachForm(self.clear_all_btn, "top", k.FORM_SPACING_Y)
        form.attachNone(self.clear_all_btn, "bottom")

        form.attachPosition(self.clear_sel_btn, "left", k.FORM_SPACING_X, 25)
        form.attachPosition(self.clear_sel_btn, "right", k.FORM_SPACING_X, 50)
        form.attachForm(self.clear_sel_btn, "top", k.FORM_SPACING_Y)
        form.attachNone(self.clear_sel_btn, "bottom")

        form.attachPosition(self.browse_file_btn, "left", k.FORM_SPACING_X, 50)
        form.attachPosition(self.browse_file_btn, "right", k.FORM_SPACING_X, 75)
        form.attachForm(self.browse_file_btn, "top", k.FORM_SPACING_Y)
        form.attachNone(self.browse_file_btn, "bottom")

        form.attachPosition(self.browse_dir_btn, "left", k.FORM_SPACING_X, 75)
        form.attachForm(self.browse_dir_btn, "right", k.FORM_SPACING_X)
        form.attachForm(self.browse_dir_btn, "top", k.FORM_SPACING_Y)
        form.attachNone(self.browse_dir_btn, "bottom")

        form.attachForm(self.scroll_list, "left", k.FORM_SPACING_X)
        form.attachForm(self.scroll_list, "right", k.FORM_SPACING_X)
        form.attachControl(
            self.scroll_list, "top", k.FORM_SPACING_Y, self.clear_sel_btn
        )
        form.attachForm(self.scroll_list, "bottom", k.FORM_SPACING_Y)

    def bind(self, attribute):
        pm.textScrollList(self.scroll_list, edit=True, removeAll=True)
        entries = list(filter(None, [element.get() for element in attribute]))
        pm.textScrollList(self.scroll_list, edit=True, append=entries)

        self.clear_all_btn.setCommand(pm.Callback(self.on_clear_all_btn, attribute))
        self.clear_sel_btn.setCommand(pm.Callback(self.on_clear_sel_btn, attribute))
        self.browse_file_btn.setCommand(pm.Callback(self.on_browse_btn, attribute, DIALOG_MODE_FILES))
        self.browse_dir_btn.setCommand(pm.Callback(self.on_browse_btn, attribute, DIALOG_MODE_FOLDER))

    def on_clear_all_btn(self, attribute):
        for element in attribute:
            pm.removeMultiInstance(element, b=True)
        pm.textScrollList(self.scroll_list, edit=True, removeAll=True)

    def on_clear_sel_btn(self, attribute):
        sel_indices = [
            i - 1
            for i in pm.textScrollList(self.scroll_list, q=True, selectIndexedItem=True)
        ]
        logical_indices = attribute.getArrayIndices()
        for i in sel_indices:
            pm.removeMultiInstance(attribute[logical_indices[i]], b=True)
        self.rebuild_ui_list(attribute)

    def on_browse_btn(self, attribute, mode):
        caption = "Choose Files" if mode == DIALOG_MODE_FILES else "Choose Folder"
        entries = pm.fileDialog2(
            caption=caption,
            okCaption="Choose",
            fileFilter="*",
            dialogStyle=2,
            fileMode=mode,
            dir=pm.workspace.getPath(),
        )
        if entries:
            logical_indices = attribute.getArrayIndices()
            next_index = logical_indices[-1] + 1 if logical_indices else 0
            for entry in entries:
                attribute[next_index].set(entry)
                next_index += 1
            self.rebuild_ui_list(attribute)

            return
        pm.displayWarning("No files Selected")

    def rebuild_ui_list(self, attribute):
        pm.textScrollList(self.scroll_list, edit=True, removeAll=True)
        entries = list(filter(None, [element.get() for element in attribute]))
        pm.textScrollList(self.scroll_list, edit=True, append=entries)
