import customtkinter as ctk

from test2va.gui.root.pages.profile_page.action_frame import ProfileActionFrameWidget
from test2va.gui.root.pages.profile_page.list import ProfileListFrameWidget
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

list_col = 0
list_row = 0
list_sticky = "nsew"
list_padx = entry_padx
list_pady = 5

action_col = 0
action_row = 1
action_sticky = "sew"
action_pady = 5


class ProfilePageWidget(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=corner_rad, border_width=border_width, fg_color=fg)

        self.grid_columnconfigure(cols, weight=c_weight)
        self.grid_rowconfigure(rows, weight=r_weight)

        self.list_frame = ProfileListFrameWidget(self)
        self.list_frame.grid(column=list_col, row=list_row, sticky=list_sticky, padx=list_padx, pady=list_pady)

        self.action_frame = ProfileActionFrameWidget(self)
        self.action_frame.grid(column=action_col, row=action_row, sticky=action_sticky, pady=action_pady)

        if ctk.get_appearance_mode() == "Light":
            self.config_light()

    def config_light(self):
        self.configure(fg_color=light_fg)
