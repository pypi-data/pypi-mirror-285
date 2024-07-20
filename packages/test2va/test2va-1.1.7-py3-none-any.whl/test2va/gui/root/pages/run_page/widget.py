import customtkinter as ctk

from test2va.gui.root.pages.run_page.output import RunPageOutputWidget
from test2va.gui.root.pages.run_page.run import RunPageRunButtonWidget
from test2va.gui.shared import prof_bg, entry_padx, light_pro_bg

corner_rad = 0
border_width = 0
fg = prof_bg

# Light
light_fg = light_pro_bg

cols = 0
c_weight = 1

rows = 1
r_weight = 1

tbox_col = 0
tbox_row = 0
tbox_sticky = "nsew"

run_col = 0
run_row = 1
run_sticky = "sew"

padx = entry_padx
pady = 5


class RunPageWidget(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=prof_bg, border_width=border_width, corner_radius=corner_rad)

        self.grid_columnconfigure(cols, weight=c_weight)
        self.grid_rowconfigure(rows, weight=r_weight)

        self.output = RunPageOutputWidget(self)
        self.output.grid(row=tbox_row, column=tbox_col, sticky=tbox_sticky, padx=padx, pady=pady)

        self.run = RunPageRunButtonWidget(self)
        self.run.grid(row=run_row, column=run_col, sticky=run_sticky, padx=padx, pady=pady)

        if ctk.get_appearance_mode() == "Light":
            self.config_light()

    def config_light(self):
        self.configure(fg_color=light_fg)
