import customtkinter as ctk

from test2va.gui.shared import gen_corner_rad

corner_rad = gen_corner_rad
border_width = 0
wrap = "word"
height = 430

default_txt = "Output will be displayed here"


class RunPageOutputWidget(ctk.CTkTextbox):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=corner_rad, border_width=border_width, wrap=wrap, height=height)
        self.insert("0.0", default_txt)

        self.root = self.winfo_toplevel()
        self.root.run_out_ref = self
