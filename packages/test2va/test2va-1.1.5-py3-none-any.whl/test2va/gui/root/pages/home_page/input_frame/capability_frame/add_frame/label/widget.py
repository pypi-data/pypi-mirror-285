import customtkinter as ctk

anchor = "w"
corner_rad = 0
justify = "left"
text = "Capabilities"


class CapLabelWidget(ctk.CTkLabel):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=corner_rad, text=text, anchor=anchor, justify=justify)