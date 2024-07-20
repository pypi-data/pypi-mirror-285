import os

import customtkinter as ctk

from test2va.gui.root.windows.cap_window.button_frame import CapAddButtonFrameWidget
from test2va.gui.root.windows.cap_window.cap_desc import CapDescWidget
from test2va.gui.root.windows.cap_window.desc_label import CapAddDescLabelWidget
from test2va.gui.root.windows.cap_window.input import NewCapInputFrameWidget
from test2va.gui.root.windows.cap_window.label_frame import CapLabelFrameWidget
from test2va.gui.shared import cap_padx, cap_pady

icon_path = os.path.join(os.path.dirname(__file__), "../../assets", "openmoji-android.ico")
size_x = 500
size_y = 200
resize_x = False
resize_y = False
title = "Test2VA Add New Capabilities"
attributes = ("-topmost", True)

padx = cap_padx
pady = cap_pady

rows = 4
r_weight = 1

cols = 0
c_weight = 1

label_frame_col = 0
label_frame_row = 0
label_frame_sticky = "new"

input_frame_col = 0
input_frame_row = 1
input_frame_sticky = "new"

desc_label_col = 0
desc_label_row = 2
desc_label_sticky = "new"

cap_desc_col = 0
cap_desc_row = 3
cap_desc_sticky = "nsew"

button_col = 0
button_row = 4
button_sticky = "sew"


class CapWindowWidget(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.root = parent

        self.iconbitmap(icon_path)
        self.geometry(f"{size_x}x{size_y}")
        self.resizable(resize_x, resize_y)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.title(title)
        self.attributes(*attributes)

        self.grid_columnconfigure(cols, weight=c_weight)
        self.grid_rowconfigure(rows, weight=r_weight)

        self.label_frame = CapLabelFrameWidget(self)
        self.label_frame.grid(row=label_frame_row, column=label_frame_col, sticky=label_frame_sticky, pady=pady)

        self.input_frame = NewCapInputFrameWidget(self)
        self.input_frame.grid(row=input_frame_row, column=input_frame_col, sticky=input_frame_sticky)

        self.desc_label = CapAddDescLabelWidget(self)
        self.desc_label.grid(row=desc_label_row, column=desc_label_col, sticky=desc_label_sticky, padx=padx)

        self.cap_desc = CapDescWidget(self)
        self.cap_desc.grid(row=cap_desc_row, column=cap_desc_col, sticky=cap_desc_sticky, padx=padx)
        self.root.cap_desc_ref = self.cap_desc

        self.button_frame = CapAddButtonFrameWidget(self)
        self.button_frame.grid(row=button_row, column=button_col, sticky=button_sticky, pady=pady)

    def on_closing(self):
        self.root.cap_window_open = False
        self.destroy()
