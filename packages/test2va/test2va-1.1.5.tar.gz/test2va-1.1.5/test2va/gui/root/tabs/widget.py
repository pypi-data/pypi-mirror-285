import os

import customtkinter as ctk

from test2va.gui.root.pages.home_page import HomePageWidget
from test2va.gui.root.pages.info_page.widget import InfoPageWidget
from test2va.gui.root.pages.profile_page import ProfilePageWidget
from test2va.gui.root.pages.run_page import RunPageWidget
from test2va.gui.root.pages.stats_page import StatsPageWidget
from test2va.gui.root.tabs.tab.widget import TabWidget
from test2va.gui.root.tabs.tab_data import TabData
from test2va.gui.shared import menu_bg

corner_rad = 0
border_width = 0

home_tab = TabData("Home", "openmoji-home.png", HomePageWidget)
prof_tab = TabData("Profiles", "openmoji-bust.png", ProfilePageWidget)
run_tab = TabData("Run", "openmoji-play.png", RunPageWidget)
stats_tab = TabData("Stats", "openmoji-chart.png", StatsPageWidget)
info_tab = TabData("Info", "openmoji-info.png", InfoPageWidget)

tabs = [home_tab, prof_tab, run_tab, stats_tab, info_tab]
def_tab = 0

tab_grid = "ew"

r_weight = 1


class TabFrameWidget(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=menu_bg, corner_radius=corner_rad, border_width=border_width)

        self.grid_rowconfigure(len(tabs), weight=r_weight)

        for i in range(len(tabs)):
            tab = tabs[i]
            tab = TabWidget(self, tab.name, tab.icon, tab.page)
            tab.grid(sticky=tab_grid)

            if i == def_tab:
                tab.on_click()
