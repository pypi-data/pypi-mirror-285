import customtkinter as ctk

from test2va.gui.root.pages.home_page.input_frame import HomeInputFrameWidget
from test2va.gui.root.pages.home_page.java_src import JavaSrcFrameWidget

corner_rad = 0
border_width = 0

rows = [1]
cols = [5, 1]

sticky = "nsew"

home_page_row = 0
home_page_col = 0

java_src_row = 0
java_src_col = 1


class HomePageWidget(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=corner_rad, border_width=border_width)

        for i in range(len(rows)):
            self.grid_rowconfigure(i, weight=rows[i])

        for i in range(len(cols)):
            self.grid_columnconfigure(i, weight=cols[i])

        self.root = self.winfo_toplevel()

        self.home_page = HomeInputFrameWidget(self)
        self.home_page.grid(row=home_page_row, column=home_page_col, sticky=sticky)

        self.root.i_frame_ref = self.home_page

        self.java_src_frame = JavaSrcFrameWidget(self)
        self.java_src_frame.grid(row=java_src_row, column=java_src_col, sticky=sticky)
