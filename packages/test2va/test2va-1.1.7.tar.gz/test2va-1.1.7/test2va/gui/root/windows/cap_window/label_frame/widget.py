import customtkinter as ctk

from test2va.gui.root.windows.cap_window.label_frame.label import CapAddLabelWidget
from test2va.gui.shared import cap_padx

corner_rad = 0
border_width = 0
fg = "transparent"

cols = [1, 1]
rows = [0]

label_row = 0
label_sticky = "nsew"
padx = cap_padx

labels = ["Select Capability", "Capability Value"]


class CapLabelFrameWidget(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=corner_rad, border_width=border_width, fg_color=fg)

        for i in range(len(rows)):
            self.grid_rowconfigure(i, weight=rows[i])

        for i in range(len(cols)):
            self.grid_columnconfigure(i, weight=cols[i])

        for i in range(len(labels)):
            label = CapAddLabelWidget(self, text=labels[i])
            label.grid(row=label_row, column=i, sticky=label_sticky, padx=padx)
