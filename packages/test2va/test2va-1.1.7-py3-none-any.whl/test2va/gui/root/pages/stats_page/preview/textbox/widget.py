import customtkinter as ctk

from test2va.gui.shared import gen_corner_rad

border_width = 0
wrap = "none"
border_spacing = 0
corner_rad = 4
width = 300

def_text = "Stats will appear here"


class StatsPreviewTextboxWidget(ctk.CTkTextbox):
    def __init__(self, parent):
        super().__init__(parent, wrap=wrap, corner_radius=corner_rad, border_width=border_width, width=width,
                         border_spacing=border_spacing)

        self.root = self.winfo_toplevel()
        self.insert("0.0", def_text)
