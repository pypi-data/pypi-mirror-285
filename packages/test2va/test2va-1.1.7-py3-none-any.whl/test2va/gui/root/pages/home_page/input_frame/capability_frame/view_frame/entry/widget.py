import customtkinter as ctk

from test2va.gui.root.pages.home_page.input_frame.capability_frame.view_frame.entry.button import CapEntryRemoveWidget
from test2va.gui.root.pages.home_page.input_frame.capability_frame.view_frame.entry.label import CapEntryLabelWidget
from test2va.gui.shared import gen_corner_rad, menu_hover, light_menu_bg

corner_rad = gen_corner_rad
border_width = 0
fg = menu_hover

# Light
light_fg = light_menu_bg

cols = 1
c_weight = 1

rows = 0
r_weight = 1

label_col = 0
label_row = 0
label_padx = 4
label_pady = 2

button_col = 1
button_row = 0
button_padx = 2
button_pady = 2

sticky = "nsew"


class CapEntryFrameWidget(ctk.CTkFrame):
    def __init__(self, parent, cap, val):
        super().__init__(parent, corner_radius=corner_rad, border_width=border_width, fg_color=fg)

        self.columnconfigure(cols, weight=c_weight)
        self.rowconfigure(rows, weight=r_weight)

        self.cap_label = CapEntryLabelWidget(self, text=f"{cap}: {val}")
        self.cap_label.grid(column=label_col, row=label_row, padx=label_padx, pady=label_pady, sticky=sticky)

        self.cap_button = CapEntryRemoveWidget(self, cap)
        self.cap_button.grid(column=button_col, row=button_row, padx=button_padx, pady=button_pady, sticky=sticky)

        if ctk.get_appearance_mode() == "Light":
            self.config_light()

    def config_light(self):
        self.configure(fg_color=light_fg)