import customtkinter as ctk

from test2va.gui.shared import gen_corner_rad

corner_rad = gen_corner_rad


class SaveProfButtonWidget(ctk.CTkButton):
    def __init__(self, parent, text, command):
        super().__init__(parent, text=text, command=command, corner_radius=corner_rad)
