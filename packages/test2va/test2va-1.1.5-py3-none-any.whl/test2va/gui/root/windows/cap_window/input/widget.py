import customtkinter as ctk

from test2va.gui.root.windows.cap_window.input.cap_entry import NewCapInputCapWidget
from test2va.gui.root.windows.cap_window.input.value_entry import NewCapInputCapValueWidget
from test2va.gui.shared import cap_padx

corner_rad = 0
border_width = 0
fg = "transparent"

cols = [1, 1]
rows = [1]

cap_col = 0
cap_row = 0

value_col = 1
value_row = 0

sticky = "nsew"
padx = cap_padx


class NewCapInputFrameWidget(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=corner_rad, border_width=border_width, fg_color=fg)

        for i in range(len(rows)):
            self.grid_rowconfigure(i, weight=rows[i])

        for i in range(len(cols)):
            self.grid_columnconfigure(i, weight=cols[i])

        self.root = self.winfo_toplevel().root

        self.cap_entry = NewCapInputCapWidget(self)
        # Gridding is handled in the widget
        self.root.cap_ref = self.cap_entry

        self.value_entry = NewCapInputCapValueWidget(self)
        self.value_entry.grid(row=value_row, column=value_col, sticky=sticky, padx=padx)
        self.root.cap_val_ref = self.value_entry
