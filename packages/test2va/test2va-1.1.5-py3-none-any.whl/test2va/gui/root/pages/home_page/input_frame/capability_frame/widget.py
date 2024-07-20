import customtkinter as ctk

from test2va.gui.root.pages.home_page.input_frame.capability_frame.add_frame import CapAddFrameWidget
from test2va.gui.root.pages.home_page.input_frame.capability_frame.view_frame import CapViewFrameWidget

corner_rad = 0
border_width = 0
fg = "transparent"

cols = [1]
rows = [1, 0]

sticky = "ew"

add_frame_col = 0
add_frame_row = 0

view_frame_col = 0
view_frame_row = 1
view_frame_sticky = "new"


class CapFrameWidget(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=corner_rad, border_width=border_width, fg_color=fg)

        for i in range(len(rows)):
            self.grid_rowconfigure(i, weight=rows[i])

        for i in range(len(cols)):
            self.grid_columnconfigure(i, weight=cols[i])

        self.add_frame = CapAddFrameWidget(self)
        self.add_frame.grid(column=add_frame_col, row=add_frame_row, sticky=sticky)

        self.view_frame = CapViewFrameWidget(self)
        self.view_frame.grid(column=view_frame_col, row=view_frame_row, sticky=view_frame_sticky)