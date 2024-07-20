import customtkinter as ctk

from test2va.gui.shared import gen_corner_rad

corner_rad = gen_corner_rad
border_width = 0
wrap = "word"
height = 70

def_text = "Select a capability to view its description"


class CapDescWidget(ctk.CTkTextbox):
    def __init__(self, parent):
        super().__init__(parent, wrap=wrap, height=height, corner_radius=corner_rad, border_width=border_width)

        self.insert("0.0", def_text)
