import customtkinter as ctk

state = "disabled"


class ProfileActionButtonWidget(ctk.CTkButton):
    def __init__(self, parent, text, command):
        super().__init__(parent, text=text, command=command, state=state)
