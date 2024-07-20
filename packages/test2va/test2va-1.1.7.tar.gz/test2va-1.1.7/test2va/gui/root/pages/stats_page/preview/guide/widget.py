from typing import Literal

import customtkinter as ctk

from test2va.gui.root.pages.stats_page.preview.guide.tab import StatsGuideTabWidget
from test2va.gui.shared import prof_bg, light_pro_bg
from test2va.gui.shared.structs import HoverScrollableFrame

corner_rad = 2
border_width = 0
orientation: Literal["horizontal"] = "horizontal"
height = 20
fg = prof_bg

# Light
light_fg = light_pro_bg

scroll_height = 3

cols = 1
c_weight = 1

rows = 0
r_weight = 1

tab_row = 0

padx = 1


class StatsPreviewGuideFrame(HoverScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=corner_rad, border_width=border_width, orientation=orientation,
                         height=height, fg_color=fg)

        self._scrollbar.configure(height=scroll_height)
        self.selected = None
        self.cols = 0
        self.tabs = []

        self.columnconfigure(cols, weight=c_weight)
        self.rowconfigure(rows, weight=r_weight)

        self.root = self.winfo_toplevel()
        self.root.stat_guide_ref = self

        if ctk.get_appearance_mode() == "Light":
            self.config_light()

    def add_tab(self, text: str, path: str, content=None):
        tab = StatsGuideTabWidget(self, text, path, content)
        tab.grid(row=tab_row, column=self.cols, padx=padx)
        self.cols += 1

        self.tabs.append(tab)

    def clear_tabs(self):
        for tab in self.tabs:
            tab.destroy()
        self.cols = 0
        self.tabs = []

        self.selected = None

    def config_light(self):
        self.configure(fg_color=light_fg)
