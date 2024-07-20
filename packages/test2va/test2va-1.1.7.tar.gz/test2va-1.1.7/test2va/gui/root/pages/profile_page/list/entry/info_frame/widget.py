import os.path

import customtkinter as ctk

from test2va.gui.root.pages.profile_page.list.entry.info_frame.labels import ProfEntryLabelInfoWidget

corner_rad = 0
border_width = 0
fg = "transparent"

rows = [1, 1, 1, 1]
cols = [1]

sticky = "nsew"


class ProfEntryInfoFrameWidget(ctk.CTkFrame):
    def __init__(self, parent, java, apk, udid, caps):
        super().__init__(parent, corner_radius=corner_rad, border_width=border_width, fg_color=fg)

        for i in range(len(rows)):
            self.grid_rowconfigure(i, weight=rows[i])

        for i in range(len(cols)):
            self.grid_columnconfigure(i, weight=cols[i])

        j_file_name = os.path.basename(java)
        if j_file_name == "java_src_code.java":
            j_file_name = "Pasted Java Code"

        labels = [j_file_name, os.path.basename(apk), udid, f"Capabilties: {len(caps)}"]

        for i, label in enumerate(labels):
            ProfEntryLabelInfoWidget(self, text=label).grid(column=0, row=i, sticky=sticky)
