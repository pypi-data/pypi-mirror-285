import customtkinter as ctk

from test2va.gui.root.pages.stats_page.preview.guide import StatsPreviewGuideFrame
from test2va.gui.root.pages.stats_page.preview.textbox import StatsPreviewTextboxWidget

border_width = 0
corner_rad = 0
fg = "transparent"

cols = 0
c_weight = 1

rows = 1
r_weight = 1

guide_col = 0
guide_row = 0

textbox_col = 0
textbox_row = 1

sticky = "nsew"
pady = 0


class StatsPreviewWidget(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=fg, border_width=border_width, corner_radius=corner_rad)

        self.columnconfigure(cols, weight=c_weight)
        self.rowconfigure(rows, weight=r_weight)

        self.root = self.winfo_toplevel()

        self.guide = StatsPreviewGuideFrame(self)
        self.guide.grid(row=guide_row, column=guide_col, sticky=sticky, pady=pady)

        self.textbox = StatsPreviewTextboxWidget(self)
        self.textbox.grid(row=textbox_row, column=textbox_col, sticky=sticky)

        self.root.stat_prev_ref = self.textbox
