import os


class TabData:
    def __init__(self, name: str, icon: str, page: object):
        self.icon = os.path.join(os.path.dirname(__file__), "./assets", icon)
        self.page = page
        self.name = name
