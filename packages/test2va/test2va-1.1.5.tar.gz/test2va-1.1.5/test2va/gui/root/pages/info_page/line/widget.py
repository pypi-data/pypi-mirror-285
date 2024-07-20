import os
import webbrowser

import customtkinter as ctk

from PIL import Image

from test2va.gui.shared import gen_corner_rad

corner_rad = gen_corner_rad
font = ("Roboto", 20)

img_path = os.path.join(os.path.dirname(__file__), "assets", "openmoji-link.png")
img_size = (20, 20)

height = 100


class InfoPageLineWidget(ctk.CTkButton):
    def __init__(self, parent, text, link=None):
        self.img = ctk.CTkImage(Image.open(img_path).resize(img_size))
        super().__init__(parent, text=text, corner_radius=corner_rad, image=self.img if link is not None else None,
                         command=self.link_click if link is not None else None, height=height, font=font)

        self.link = link

    def link_click(self):
        webbrowser.open_new(self.link)
