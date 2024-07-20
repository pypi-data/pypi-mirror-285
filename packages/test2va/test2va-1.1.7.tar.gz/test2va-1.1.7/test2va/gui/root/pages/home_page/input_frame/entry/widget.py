import customtkinter as ctk

from test2va.gui.root.pages.home_page.input_frame.entry.browse import HomeEntryBrowseWidget
from test2va.gui.root.pages.home_page.input_frame.entry.input import HomeEntryInputWidget
from test2va.gui.root.pages.home_page.input_frame.entry.label import HomeEntryLabelWidget
from test2va.gui.root.pages.home_page.input_frame.entry.udid import HomeEntryRefreshUDIDWidget
from test2va.gui.shared import entry_label_padx, small_button_padx

corner_rad = 0
border_width = 0
fg = "transparent"

cols = [20, 1]
colspan = 2
rows = 1
r_weight = 1

sticky = "ew"

label_padx = entry_label_padx
label_col = 0
label_row = 0

input_col = 0
input_row = 1

browse_col = 1
browse_row = 1
browse_padx = small_button_padx


class HomeEntryFrameWidget(ctk.CTkFrame):
    def __init__(self, parent, label_text: str, entry_text: str, browse_cmd=None, refresh_cmd=None):
        super().__init__(parent, corner_radius=corner_rad, border_width=border_width, fg_color=fg)

        for i in range(len(cols)):
            self.grid_columnconfigure(i, weight=cols[i])

        self.grid_rowconfigure(rows, weight=r_weight)

        self.label = HomeEntryLabelWidget(self, label_text)
        self.label.grid(sticky=sticky, row=label_row, column=label_col, padx=label_padx)

        self.input = HomeEntryInputWidget(self, entry_text)

        if browse_cmd is not None:
            self.input.grid(sticky=sticky, row=input_row, column=input_col)

            self.browse_button = HomeEntryBrowseWidget(self, lambda: browse_cmd(self.input))
            self.browse_button.grid(sticky=sticky, row=browse_row, column=browse_col, padx=browse_padx)
        elif refresh_cmd is not None:
            self.input.grid(sticky=sticky, row=input_row, column=input_col)

            self.refresh_button = HomeEntryRefreshUDIDWidget(self, lambda: refresh_cmd())
            self.refresh_button.grid(sticky=sticky, row=browse_row, column=browse_col, padx=browse_padx)
        else:
            self.input.grid(sticky=sticky, row=input_row, column=input_col, columnspan=colspan)
