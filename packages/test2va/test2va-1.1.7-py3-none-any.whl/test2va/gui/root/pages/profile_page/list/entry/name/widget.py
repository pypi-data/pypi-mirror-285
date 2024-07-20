import customtkinter as ctk

corner_rad = 0
anchor = "w"
justify = "left"
fg = "transparent"
font = prof_name_font = ("Roboto", 30)


class ProfEntryNameLabelWidget(ctk.CTkLabel):
    def __init__(self, parent, name):
        super().__init__(parent, text=name, corner_radius=corner_rad, anchor=anchor, justify=justify, fg_color=fg,
                         font=font)