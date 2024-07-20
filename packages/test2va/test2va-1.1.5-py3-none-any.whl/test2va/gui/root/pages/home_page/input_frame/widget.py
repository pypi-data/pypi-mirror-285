import customtkinter as ctk
import tkinter as tk

from test2va.bridge.appium import find_running_device
from test2va.gui.root.pages.home_page.input_frame.browse import java_browse, browse
from test2va.gui.root.pages.home_page.input_frame.capability_frame import CapFrameWidget
from test2va.gui.root.pages.home_page.input_frame.entry.widget import HomeEntryFrameWidget
from test2va.gui.root.pages.home_page.input_frame.save_button import SaveButtonWidget
from test2va.gui.shared import entry_padx, def_java_entry, def_udid_entry

corner_rad = 0
border_width = 0

cols = 0
rows = 4

java_label = "Java File"
java_entry = def_java_entry
java_col = 0
java_row = 0

apk_label = "APK File"
apk_entry = "Path to app APK"
apk_file = [("APK files", "*.apk")]
apk_col = 0
apk_row = 1

udid_label = def_udid_entry
udid_col = 0
udid_row = 2

cap_col = 0
cap_row = 3

sav_col = 0
sav_row = 4
sav_sticky = "nsew"

padx = entry_padx
pady = 5

sticky = "new"


class HomeInputFrameWidget(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=corner_rad, border_width=border_width)
        self.root = self.winfo_toplevel()
        self.grid_columnconfigure(cols, weight=1)
        self.grid_rowconfigure(rows, weight=1)

        java_cmd = lambda text: java_browse(text, self.root.java_src_ref, self.unbind_mod_java, self.bind_mod_java)
        apk_cmd = lambda text: browse(text, apk_file)

        def udid_cmd():
            devices = find_running_device()
            udid_entry = len(devices) > 0 and devices[0] or udid_label
            self.udid_entry.input.delete(0, tk.END)
            self.udid_entry.input.insert(0, udid_entry)

        devices = find_running_device()
        udid_entry = len(devices) > 0 and devices[0] or udid_label

        # Inputs
        self.java_entry = HomeEntryFrameWidget(self, label_text=java_label, entry_text=java_entry, browse_cmd=java_cmd)
        self.apk_entry = HomeEntryFrameWidget(self, label_text=apk_label, entry_text=apk_entry, browse_cmd=apk_cmd)
        self.udid_entry = HomeEntryFrameWidget(self, label_text=udid_label, entry_text=udid_entry, refresh_cmd=udid_cmd)

        self.java_entry.grid(column=java_col, row=java_row, sticky=sticky, padx=padx, pady=pady)
        self.apk_entry.grid(column=apk_col, row=apk_row, sticky=sticky, padx=padx, pady=pady)
        self.udid_entry.grid(column=udid_col, row=udid_row, sticky=sticky, padx=padx, pady=pady)

        self.root.java_path_ref = self.java_entry.input

        # Capabilities
        self.capability_frame = CapFrameWidget(self)
        self.capability_frame.grid(column=cap_col, row=cap_row, sticky=sticky, padx=padx, pady=pady)

        # Save Profile
        self.save_button = SaveButtonWidget(self)
        self.save_button.grid(column=sav_col, row=sav_row, sticky=sav_sticky, padx=padx, pady=pady)

    def bind_mod_java(self):
        self.root.java_window_content = self.root.java_src_ref.get("0.0", "end-1c")
        self.root.java_src_ref.bind("<<Modified>>", self.java_text_change)

    def unbind_mod_java(self):
        self.root.java_src_ref.unbind("<<Modified>>")

    def java_text_change(self, _event):
        new_content = self.root.java_src_ref.get("0.0", "end-1c")
        input_widget = self.java_entry.input

        if new_content == self.root.java_window_content:
            self.root.java_src_ref.edit_modified(False)
            return

        input_widget.delete(0, tk.END)
        self.root.java_window_content = new_content
        self.root.java_src_ref.edit_modified(False)
