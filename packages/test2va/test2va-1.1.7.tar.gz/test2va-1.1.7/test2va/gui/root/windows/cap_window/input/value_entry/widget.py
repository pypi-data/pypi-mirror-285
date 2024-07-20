import customtkinter as ctk

from test2va.gui.shared import gen_corner_rad

corner_rad = gen_corner_rad

def_val = "Integer"


class NewCapInputCapValueWidget(ctk.CTkEntry):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=corner_rad)
        self.insert(0, def_val)
