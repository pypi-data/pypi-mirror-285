import customtkinter as ctk

from test2va.gui.root.pages.home_page.java_src.textbox import JavaTextboxWidget
from test2va.gui.shared import entry_label_padx

corner_rad = 0
border_width = 0

cols = [1]
rows = [1]

sticky = "nsew"
padx = entry_label_padx
pady = entry_label_padx


class JavaSrcFrameWidget(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=corner_rad, border_width=border_width)

        for i in range(len(rows)):
            self.grid_rowconfigure(i, weight=rows[i])

        for i in range(len(cols)):
            self.grid_columnconfigure(i, weight=cols[i])

        self.textbox = JavaTextboxWidget(self)
        self.textbox.grid(sticky=sticky, padx=padx, pady=pady)

        self.winfo_toplevel().java_src_ref = self.textbox
