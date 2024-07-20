import customtkinter as ctk

from test2va.gui.shared import gen_corner_rad

corner_rad = gen_corner_rad


class SaveProfEntryWidget(ctk.CTkEntry):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=corner_rad)

        self.root = parent.winfo_toplevel().root

        if self.root.loaded_profile:
            self.insert(0, self.root.loaded_profile)
