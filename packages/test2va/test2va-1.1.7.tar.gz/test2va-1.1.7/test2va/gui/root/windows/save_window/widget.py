import os

import customtkinter as ctk

from test2va.gui.root.windows.save_window.button_frame import SaveProfButtonFrameWidget
from test2va.gui.root.windows.save_window.entry import SaveProfEntryWidget
from test2va.gui.root.windows.save_window.label import SaveProfLabelWidget
from test2va.gui.shared import entry_padx

icon_path = os.path.join(os.path.dirname(__file__), "../../assets", "openmoji-android.ico")
size_x = 400
size_y = 115
resize_x = False
resize_y = False
title = "Test2VA Save Profile"
attributes = ("-topmost", True)

rows = 2
r_weight = 1

cols = 0
c_weight = 1

label_col = 0
label_row = 0
label_sticky = "nsew"
label_padx = entry_padx
label_pady = 5

entry_col = 0
entry_row = 1
entry_sticky = "nsew"
entry_padx = 5

button_col = 0
button_row = 2
button_sticky = "sew"
button_pady = 5


class SaveProfWinWidget(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.root = parent

        self.iconbitmap(icon_path)
        self.geometry(f"{size_x}x{size_y}")
        self.resizable(resize_x, resize_y)
        self.title(title)
        self.attributes(*attributes)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.grid_columnconfigure(cols, weight=c_weight)
        self.grid_rowconfigure(rows, weight=r_weight)

        self.label = SaveProfLabelWidget(self)
        self.label.grid(row=label_row, column=label_col, sticky=label_sticky, padx=label_padx, pady=label_pady)

        self.entry = SaveProfEntryWidget(self)
        self.entry.grid(row=entry_row, column=entry_col, sticky=entry_sticky, padx=entry_padx)

        self.button_frame = SaveProfButtonFrameWidget(self, self.entry, self.label)
        self.button_frame.grid(row=button_row, column=button_col, sticky=button_sticky, pady=button_pady)

    def on_closing(self):
        self.root.sav_prof_open = False
        self.destroy()
