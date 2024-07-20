import customtkinter as ctk

from test2va.gui.root.windows.save_window.widget import SaveProfWinWidget

text = "Save Profile"


class SaveButtonWidget(ctk.CTkButton):
    def __init__(self, parent):
        self.root = parent.winfo_toplevel()
        super().__init__(parent, text=text, command=self.save_prof_window)

    def save_prof_window(self):
        if self.root.sav_prof_open:
            return

        self.root.sav_prof_open = True

        SaveProfWinWidget(self.root)
