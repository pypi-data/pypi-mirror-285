from cwmaya.tabs.task_tab import TaskTab


class QuicktimeTab(TaskTab):

    ATTRIBUTE_PREFIX = "qtm"

    def __init__(self):
        super(QuicktimeTab, self).__init__()
        self.build_ui()
