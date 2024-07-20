import customtkinter as ctk

from test2va.gui.shared import menu_hover, cur_tab_color, menu_bg

corner_rad = 0
border_width = 0
width = 1

fg = "transparent"
hover = menu_hover
selected = cur_tab_color


class StatsGuideTabWidget(ctk.CTkButton):
    def __init__(self, parent, text: str, path: str, content=None):
        super().__init__(parent, text=text, corner_radius=corner_rad, border_width=border_width, command=self._on_click,
                         width=width, hover_color=hover, fg_color=fg)

        self.path = path
        self.content = content
        self.root = self.winfo_toplevel()
        self.parent = parent

        if ctk.get_appearance_mode() == "Light":
            self.config_light()

    def _on_click(self):
        if self.parent.selected == self:
            return

        self.configure(fg_color=selected, hover_color=selected)

        if self.parent.selected is not None:
            self.parent.selected.configure(fg_color=fg, hover_color=hover)

        self.parent.selected = self

        if self.content is not None:
            self.root.stat_prev_ref.delete("0.0", "end")
            self.root.stat_prev_ref.insert("0.0", self.content)
            return

        try:
            # Read the contents of self.path and display them to the textbox self.root.stat_prev_ref
            with open(self.path, "r") as file:
                self.root.stat_prev_ref.delete("0.0", "end")
                self.root.stat_prev_ref.insert("0.0", file.read())
        except Exception:
            pass

    def config_light(self):
        self.configure(text_color="black")