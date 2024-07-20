import customtkinter as ctk

from test2va.gui.root.pages.info_page.line import InfoPageLineWidget
from test2va.gui.shared import light_pro_bg

corner_rad = 0
border_width = 0
fg = "transparent"

# Light
light_fg = light_pro_bg

cols = [1]

rows = [1, 1, 1, 1]

col = 0

sticky = "nsew"
padx = 10
pady = 3

site_link = "https://sites.google.com/view/test2va"


class InfoPageWidget(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=fg, corner_radius=corner_rad, border_width=border_width)

        for i in range(len(rows)):
            self.grid_rowconfigure(i, weight=rows[i])

        for i in range(len(cols)):
            self.grid_columnconfigure(i, weight=cols[i])

        self.site = InfoPageLineWidget(self, text="Tool Website", link=site_link)
        self.site.grid(row=0, column=col, sticky=sticky, padx=padx, pady=pady)

        self.github = InfoPageLineWidget(self, text="GitHub Repository: Coming Soon")
        self.github.grid(row=1, column=col, sticky=sticky, padx=padx, pady=pady)

        self.docs = InfoPageLineWidget(self, text="Documentation: Coming Soon")
        self.docs.grid(row=2, column=col, sticky=sticky, padx=padx, pady=pady)

        self.email = InfoPageLineWidget(self, text="nontestname@gmail.com", link="mailto:nontestname@gmail.com")
        self.email.grid(row=3, column=col, sticky=sticky, padx=padx, pady=pady)

        if ctk.get_appearance_mode() == "Light":
            self.config_light()

    def config_light(self):
        self.configure(fg_color=light_fg)
