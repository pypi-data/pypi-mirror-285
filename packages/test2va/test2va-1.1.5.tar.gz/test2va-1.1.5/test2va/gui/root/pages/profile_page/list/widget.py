from typing import Literal

import customtkinter as ctk

from test2va.bridge import get_profiles
from test2va.gui.root.pages.profile_page.list.entry import ProfEntryFrameWidget
from test2va.gui.root.pages.profile_page.list.no_prof_label import NoProfLabelWidget
from test2va.gui.shared import gen_corner_rad
from test2va.gui.shared.structs import HoverScrollableFrame

corner_rad = gen_corner_rad
border_width = 0
orientation: Literal["vertical"] = "vertical"
height = 415

cols = 0
c_weight = 1

sticky = "new"
padx = 5
pady = 5


class ProfileListFrameWidget(HoverScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=corner_rad, border_width=border_width, orientation=orientation,
                         height=height)

        self.grid_columnconfigure(cols, weight=c_weight)

        self.winfo_toplevel().prof_list_ref = self

        self.populate_profiles()

    def populate_profiles(self):
        for widget in self.winfo_children():
            widget.destroy()

        profile = get_profiles()
        for prof in profile:
            entry = ProfEntryFrameWidget(self, prof["name"], prof["java_path"], prof["apk"], prof["udid"], prof["caps"])
            entry.grid(sticky=sticky, padx=padx, pady=pady)

        if len(profile) <= 0:
            label = NoProfLabelWidget(self)
            label.grid(sticky=sticky, padx=padx, pady=pady)
