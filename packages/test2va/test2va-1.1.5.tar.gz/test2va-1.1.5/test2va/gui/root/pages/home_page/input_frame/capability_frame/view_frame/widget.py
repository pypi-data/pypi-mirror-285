from typing import Literal

import customtkinter as ctk

from test2va.gui.root.pages.home_page.input_frame.capability_frame.view_frame.entry import CapEntryFrameWidget
from test2va.gui.shared import gen_corner_rad
from test2va.gui.shared.structs import HoverScrollableFrame

corner_rad = gen_corner_rad
border_width = 0
orientation: Literal["horizontal"] = "horizontal"
height = 185

max_rows_per_column = 4
padx = 5
pady = 5

sticky = "w"


class CapViewFrameWidget(HoverScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=corner_rad, border_width=border_width, orientation=orientation,
                         height=height)

        self.root = self.winfo_toplevel()
        self.root.cap_frame_ref = self

    def redraw_caps(self):
        for widget in self.winfo_children():
            widget.destroy()

        col = 0
        row = 0

        for cap, val in self.root.cap_cache.items():
            frame = CapEntryFrameWidget(self, cap, val)
            frame.grid(row=row, column=col, padx=padx, pady=pady, sticky=sticky)

            row += 1
            if row >= max_rows_per_column:
                row = 0
                col += 1
