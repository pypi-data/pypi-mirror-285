import customtkinter as ctk

from test2va.gui.root.tabs.tab.tab_icon import TabIconWidget
from test2va.gui.shared import menu_bg, menu_hover, menu_icon_size, cur_tab_color

icon_size = menu_icon_size

anchor = "w"
border_space = 10
corner_rad = 0
fg = menu_bg
hover = menu_hover
tab_height = 25
tab_width = 160

tab_color = cur_tab_color

new_pg_col = 1
new_pg_row = 0
new_pg_sticky = "nsew"


class TabWidget(ctk.CTkButton):

    def __init__(self, parent, name: str, icon_path: str, page: object):
        self.icon = TabIconWidget(icon_path, icon_size)
        self.page = page
        self.name = name

        super().__init__(parent, text=name, command=self.on_click, corner_radius=corner_rad, height=tab_height,
                         border_spacing=border_space, anchor=anchor, fg_color=fg, image=self.icon, width=tab_width,
                         hover_color=hover)

        self.root = self.winfo_toplevel()

    def on_click(self):
        cur_tab = self.root.cur_tab

        if cur_tab == self:
            return

        if cur_tab is not None:
            cur_tab.configure(fg_color=fg, hover_color=hover)

        self.configure(fg_color=tab_color, hover_color=tab_color)
        self.root.cur_tab = self

        cur_page = self.root.cur_page

        if cur_page is not None:
            cur_page.grid_forget()

        # If self.root.page_cache has self.name as a key, then the page is already created and stored in the cache
        if self.name in self.root.page_cache:
            new_page = self.root.page_cache[self.name]
        else:
            new_page = self.page(self.root)
            self.root.page_cache[self.name] = new_page

        new_page.grid(row=new_pg_row, column=new_pg_col, sticky=new_pg_sticky)
        self.root.cur_page = new_page
