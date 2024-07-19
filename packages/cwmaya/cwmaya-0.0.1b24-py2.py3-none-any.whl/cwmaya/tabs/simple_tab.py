from cwmaya.tabs.task_tab import TaskTab


class SimpleTab(TaskTab):
 
    def __init__(self):

        super(SimpleTab, self).__init__()
        self.build_ui()
