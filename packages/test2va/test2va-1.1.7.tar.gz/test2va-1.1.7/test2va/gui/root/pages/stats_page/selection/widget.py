from typing import Literal

import customtkinter as ctk

from test2va.bridge import get_stats
from test2va.gui.root.pages.stats_page.selection.entry import StatSelectionEntryWidget
from test2va.gui.shared import gen_corner_rad
from test2va.gui.shared.structs import HoverScrollableFrame

corner_rad = gen_corner_rad
border_width = 0
orientation: Literal["vertical"] = "vertical"
height = 415

cols = 0
c_weight = 1

rows = 1
r_weight = 1

entry_col = 0
sticky = "new"

pady = 2


class StatsSelectScrollWidget(HoverScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=corner_rad, border_width=border_width, orientation=orientation,
                         height=height)

        self.root = self.winfo_toplevel()
        self.selected = None

        self.stats = get_stats()

        self.columnconfigure(cols, weight=c_weight)
        self.rowconfigure(rows, weight=r_weight)

        self.root.stat_list_ref = self

        self.redraw_stats()

    def redraw_stats(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.stats = get_stats()

        for i in range(len(self.stats)):
            stat = self.stats[i]
            entry = StatSelectionEntryWidget(self, stat["name"], i+1)
            entry.grid(row=i, column=entry_col, sticky=sticky, pady=pady)

        if len(self.stats) < 1:
            ctk.CTkLabel(self, text="No stats found", fg_color="transparent").grid(row=0, column=0)