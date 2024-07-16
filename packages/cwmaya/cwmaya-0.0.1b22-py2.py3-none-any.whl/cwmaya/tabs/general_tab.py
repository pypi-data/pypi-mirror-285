# -*- coding: utf-8 -*-


from cwmaya.tabs.base_tab import BaseTab


class GeneralTab(BaseTab):

    def __init__(self):
        self.chunk_size_ctl = None
        self.custom_frames_ctl = None
        self.scout_frames_ctl = None
        self.frame_range_ctl = None

        super(GeneralTab, self).__init__()
        self.build_ui()

    def build_ui(self):
        """
        Create the frames controls.
        """
        self.chunk_size_ctl = self.create_int_control(self.column, "Chunk size")
        self.custom_frames_ctl = self.create_hidable_text_control(
            self.column, "Custom frames"
        )
        self.scout_frames_ctl = self.create_hidable_text_control(
            self.column, "Scout frames"
        )

    def bind(self, node):
        self.chunk_size_ctl.bind(node.attr("chunkSize"))
        self.custom_frames_ctl.bind(
            node.attr("useCustomRange"), node.attr("customRange")
        )
        self.scout_frames_ctl.bind(
            node.attr("useScoutFrames"), node.attr("scoutFrames")
        )
