from cwmaya.tabs.task_tab import TaskTab


class SlackTab(TaskTab):

    ATTRIBUTE_PREFIX = "slk"

    def __init__(self):
        super(SlackTab, self).__init__()
        self.build_ui()
