import customtkinter as ctk

from test2va.gui.root import RootWidget


class GUI:
    def __init__(self):
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("dark-blue")

        self.root = RootWidget()

        self.root.mainloop()
