import customtkinter as ctk

corner_rad = 0
anchor = "w"
justify = "left"


class CapAddLabelWidget(ctk.CTkLabel):
    def __init__(self, parent, text):
        super().__init__(parent, text=text, corner_radius=corner_rad, anchor=anchor, justify=justify)
