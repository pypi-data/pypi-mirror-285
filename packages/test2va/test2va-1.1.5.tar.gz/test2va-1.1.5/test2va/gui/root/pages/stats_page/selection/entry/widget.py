import os

import customtkinter as ctk

from test2va.bridge.stats import find_stats, get_stat_string
from test2va.gui.shared import menu_hover, cur_tab_color, prof_bg, light_menu_bg, light_menu_hover

fg = prof_bg
hover = menu_hover
selected = cur_tab_color

# Light
light_fg = light_menu_bg
light_hover = light_menu_hover

methods_folder = "generated_methods"


class StatSelectionEntryWidget(ctk.CTkButton):
    def __init__(self, parent, title: str, index: int):
        self.text = title.replace("_", " ")
        super().__init__(parent, text=self.text, command=self._on_click, hover_color=hover, fg_color=fg)

        self.index = index
        self.root = self.winfo_toplevel()
        self.parent = parent
        self.stats = find_stats(self.index)
        self.overview = get_stat_string(self.index)

        if ctk.get_appearance_mode() == "Light":
            self.config_light()

    def _on_click(self):
        if self.parent.selected == self:
            return

        theme = ctk.get_appearance_mode()
        self.configure(fg_color=selected, hover_color=selected)

        if self.parent.selected is not None:
            if theme == "Light":
                self.parent.selected.configure(fg_color=light_fg, hover_color=light_hover)
            else:
                self.parent.selected.configure(fg_color=fg, hover_color=hover)

        self.parent.selected = self

        self.root.stat_guide_ref.clear_tabs()

        self.root.stat_guide_ref.add_tab(text="Overview", path="", content=self.overview)

        gen_methods_folder = os.path.join(self.stats["path"], methods_folder)

        if not os.path.exists(gen_methods_folder):
            return

        i = 1
        for file in os.listdir(gen_methods_folder):
            if file.endswith(".txt"):
                self.root.stat_guide_ref.add_tab(text=f"Method {i}", path=os.path.join(gen_methods_folder, file))
                i += 1

    def config_light(self):
        self.configure(fg_color=light_fg, hover_color=light_hover, text_color="black")
