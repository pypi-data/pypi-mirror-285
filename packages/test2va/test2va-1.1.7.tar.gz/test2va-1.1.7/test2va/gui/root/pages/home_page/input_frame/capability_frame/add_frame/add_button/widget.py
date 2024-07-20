import os

import customtkinter as ctk

from PIL import Image

from test2va.gui.root.windows.cap_window.widget import CapWindowWidget
from test2va.gui.shared import menu_icon_size, gen_corner_rad, small_button_size

img_path = os.path.join(os.path.dirname(__file__), "assets", "openmoji-plus.png")
img_size = menu_icon_size

text = ""
corner_rad = gen_corner_rad
width = small_button_size
height = small_button_size


class CapAddButtonWidget(ctk.CTkButton):
    def __init__(self, parent):
        self.root = parent.winfo_toplevel()
        self.img = ctk.CTkImage(Image.open(img_path).resize(img_size))
        super().__init__(parent, corner_radius=corner_rad, image=self.img, text=text, width=width, height=height,
                         command=self.open_cap_window)

    def open_cap_window(self):
        if self.root.cap_window_open:
            return

        self.root.cap_window_open = True

        CapWindowWidget(self.root)
