import customtkinter as ctk

text = "No profiles saved"
corner_rad = 0
anchor = "center"
justify = "center"
fg = "transparent"


class NoProfLabelWidget(ctk.CTkLabel):
    def __init__(self, parent):
        super().__init__(parent, text=text, corner_radius=corner_rad, anchor=anchor, justify=justify, fg_color=fg)