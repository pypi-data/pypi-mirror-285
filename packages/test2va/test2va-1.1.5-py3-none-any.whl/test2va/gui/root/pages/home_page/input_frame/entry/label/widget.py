import customtkinter as ctk

corner_rad = 0
anchor = "w"
justify = "left"


class HomeEntryLabelWidget(ctk.CTkLabel):
    def __init__(self, parent, text: str):
        super().__init__(parent, text=text, corner_radius=corner_rad, anchor=anchor, justify=justify)