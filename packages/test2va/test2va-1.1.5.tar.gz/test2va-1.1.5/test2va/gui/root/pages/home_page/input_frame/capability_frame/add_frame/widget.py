import customtkinter as ctk

from test2va.gui.root.pages.home_page.input_frame.capability_frame.add_frame.add_button import CapAddButtonWidget
from test2va.gui.root.pages.home_page.input_frame.capability_frame.add_frame.label import CapLabelWidget
from test2va.gui.shared import entry_label_padx, small_button_padx

corner_rad = 0
border_width = 0
fg = "transparent"

cols = [30, 1]
rows = [1]

sticky = "ew"

cap_label_col = 0
cap_label_row = 0
cap_label_padx = entry_label_padx

add_button_col = 1
add_button_row = 0
add_button_padx = small_button_padx


class CapAddFrameWidget(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=corner_rad, border_width=border_width, fg_color=fg)

        for i in range(len(rows)):
            self.grid_rowconfigure(i, weight=rows[i])

        for i in range(len(cols)):
            self.grid_columnconfigure(i, weight=cols[i])

        self.cap_label = CapLabelWidget(self)
        self.cap_label.grid(sticky=sticky, row=cap_label_row, column=cap_label_col, padx=cap_label_padx)

        self.add_button = CapAddButtonWidget(self)
        self.add_button.grid(sticky=sticky, row=add_button_row, column=add_button_col, padx=add_button_padx)