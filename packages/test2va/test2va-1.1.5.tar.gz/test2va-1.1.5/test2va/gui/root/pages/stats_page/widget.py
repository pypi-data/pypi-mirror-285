import customtkinter as ctk

from test2va.gui.root.pages.stats_page.preview import StatsPreviewWidget
from test2va.gui.root.pages.stats_page.selection import StatsSelectScrollWidget
from test2va.gui.shared import prof_bg, entry_label_padx, entry_padx, light_pro_bg

corner_rad = 0
border_width = 0
fg = prof_bg

# Light
light_fg = light_pro_bg

rows = [1]
cols = [2, 1]

selection_row = 0
selection_col = 0
selection_padx = entry_padx

preview_row = 0
preview_col = 1
preview_padx = entry_label_padx

pady = entry_label_padx
sticky = "nsew"


class StatsPageWidget(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=prof_bg, border_width=border_width, corner_radius=corner_rad)

        for i in range(len(rows)):
            self.grid_rowconfigure(i, weight=rows[i])

        for i in range(len(cols)):
            self.grid_columnconfigure(i, weight=cols[i])

        self.root = self.winfo_toplevel()

        self.selection = StatsSelectScrollWidget(self)
        self.selection.grid(row=selection_row, column=selection_col, sticky=sticky, padx=selection_padx, pady=pady)

        self.preview = StatsPreviewWidget(self)
        self.preview.grid(row=preview_row, column=preview_col, sticky=sticky, padx=preview_padx, pady=pady)

        if ctk.get_appearance_mode() == "Light":
            self.config_light()

    def config_light(self):
        self.configure(fg_color=light_fg)
