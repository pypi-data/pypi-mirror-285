import customtkinter as ctk

from test2va.gui.root.pages.profile_page.list.entry.info_frame import ProfEntryInfoFrameWidget
from test2va.gui.root.pages.profile_page.list.entry.name import ProfEntryNameLabelWidget
from test2va.gui.shared import gen_corner_rad, prof_bg, cur_tab_color, menu_hover, light_menu_bg, light_menu_hover

corner_rad = gen_corner_rad
fg = prof_bg
hover = menu_hover
selected = cur_tab_color

# Light
light_fg = light_menu_bg
light_hover = light_menu_hover

cols = [1, 1]
rows = [1]

name_col = 0
name_row = 0
name_sticky = "nsew"

info_col = 1
info_row = 0
info_sticky = "nsew"

padx = 5
pady = 5


class ProfEntryFrameWidget(ctk.CTkFrame):
    def __init__(self, parent, name, java, apk, udid, caps):
        super().__init__(parent, corner_radius=corner_rad, fg_color=fg)

        self.root = self.winfo_toplevel()
        self.name = name
        self.parent = parent

        for i in range(len(rows)):
            self.grid_rowconfigure(i, weight=rows[i])

        for i in range(len(cols)):
            self.grid_columnconfigure(i, weight=cols[i])

        self.name_label = ProfEntryNameLabelWidget(self, name)
        self.name_label.grid(column=name_col, row=name_row, sticky=name_sticky, padx=padx, pady=pady)

        self.info_frame = ProfEntryInfoFrameWidget(self, java, apk, udid, caps)
        self.info_frame.grid(column=info_col, row=info_row, sticky=info_sticky, padx=padx, pady=pady)

        self.bind_events()

        if ctk.get_appearance_mode() == "Light":
            self.config_light()

    def activate_buttons(self):
        for button in self.root.prof_butt_ref:
            button.configure(state="normal")

    def on_enter(self, _event):
        if self.cget("fg_color") == selected:
            return

        theme = ctk.get_appearance_mode()

        self.configure(fg_color=hover if theme == "Dark" else light_hover)

    def on_leave(self, _event):
        if self.cget("fg_color") == selected:
            return

        theme = ctk.get_appearance_mode()

        self.configure(fg_color=fg if theme == "Dark" else light_fg)

    def on_click(self, _event):
        self.activate_buttons()
        self.root.selected_profile = self.name

        theme = ctk.get_appearance_mode()

        for child in self.parent.winfo_children():
            child.configure(fg_color=fg if theme == "Dark" else light_fg)

        self.configure(fg_color=selected)

    def bind_events(self, widget=None):
        if widget is None:
            widget = self

        widget.bind("<Enter>", self.on_enter)
        widget.bind("<Leave>", self.on_leave)
        widget.bind("<Button-1>", self.on_click)
        for child in widget.winfo_children():
            self.bind_events(child)

    def config_light(self):
        self.configure(fg_color=light_fg)
