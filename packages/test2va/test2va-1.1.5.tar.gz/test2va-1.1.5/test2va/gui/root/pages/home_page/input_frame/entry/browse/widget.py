import os

import customtkinter as ctk

from PIL import Image

from test2va.gui.shared import menu_icon_size, gen_corner_rad, small_button_size

icon_path = os.path.join(os.path.dirname(__file__), "./assets", "openmoji-folder.png")
icon_size = menu_icon_size

text = ""
corner_rad = gen_corner_rad
height = small_button_size
width = small_button_size


class HomeEntryBrowseWidget(ctk.CTkButton):

    def __init__(self, parent, browse_cmd):
        self.icon = ctk.CTkImage(Image.open(icon_path).resize(icon_size))
        super().__init__(parent, text=text, image=self.icon, corner_radius=corner_rad, height=height, width=width,
                         command=browse_cmd)
