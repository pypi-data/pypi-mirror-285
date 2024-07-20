import os

import customtkinter as ctk

from PIL import Image

from test2va.gui.shared import menu_icon_size, menu_hover

icon_path = os.path.join(os.path.dirname(__file__), "./assets", "openmoji-x.png")
icon_size = menu_icon_size

width = 10
hover_color = menu_hover
height = 10
fg_color = "transparent"
corner_radius = 0
text = ""


class CapEntryRemoveWidget(ctk.CTkButton):
    def __init__(self, parent, cap):
        self.icon = ctk.CTkImage(Image.open(icon_path).resize(icon_size))
        super().__init__(parent, width=width, height=height, corner_radius=corner_radius, fg_color=fg_color,
                         hover_color=hover_color, image=self.icon, text=text, command=self.remove_cap)
        self.cap = cap
        self.root = self.winfo_toplevel()

    def remove_cap(self):
        self.root.cap_cache.pop(self.cap)
        self.root.cap_frame_ref.redraw_caps()
