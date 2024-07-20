import customtkinter as ctk
import tkinter as tk

from test2va.bridge import find_profile, delete_profile
from test2va.gui.root.pages.profile_page.action_frame.buttons import ProfileActionButtonWidget
from test2va.gui.shared import entry_label_padx

corner_rad = 0
border_width = 0
fg = "transparent"

cols = [4, 1]
rows = [1]

load_prof_col = 0
load_prof_row = 0

delete_prof_col = 1
delete_prof_row = 0
delete_prof_fg = "red"

sticky = "nsew"
padx = entry_label_padx


class ProfileActionFrameWidget(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        for i in range(len(rows)):
            self.grid_rowconfigure(i, weight=rows[i])

        for i in range(len(cols)):
            self.grid_columnconfigure(i, weight=cols[i])

        self.root = self.winfo_toplevel()

        self.load_prof = ProfileActionButtonWidget(self, text="Load Profile", command=self.load_profile)
        self.load_prof.grid(column=load_prof_col, row=load_prof_row, sticky=sticky, padx=padx)

        self.delete_prof = ProfileActionButtonWidget(self, text="Delete Profile", command=self.delete_profile)
        self.delete_prof.grid(column=delete_prof_col, row=delete_prof_row, sticky=sticky, padx=padx)
        self.delete_prof.configure(fg_color=delete_prof_fg)

        self.root.prof_butt_ref = [self.load_prof, self.delete_prof]

    def load_profile(self):
        profile = find_profile(str(self.root.selected_profile))

        if profile is None:
            return

        self.root.loaded_profile = profile["name"]

        iframe = self.root.i_frame_ref
        iframe.java_entry.input.delete(0, tk.END)
        iframe.java_entry.input.insert(0, profile["java_path"])
        iframe.java_entry.input.xview(tk.END)

        iframe.apk_entry.input.delete(0, tk.END)
        iframe.apk_entry.input.insert(0, profile["apk"])
        iframe.apk_entry.input.xview(tk.END)

        iframe.udid_entry.input.delete(0, tk.END)
        iframe.udid_entry.input.insert(0, profile["udid"])

        self.root.cap_cache = {cap: str(val) for cap, val in profile["caps"].items()}

        self.root.cap_frame_ref.redraw_caps()

        java_window = self.root.java_src_ref
        try:
            with open(profile["java_path"], "r") as f:
                java_window.delete("0.0", "end")
                java_window.insert("0.0", f.read())
                self.root.java_window_content = java_window.get("0.0", "end-1c")
        except Exception:
            java_window.delete("0.0", "end")
            java_window.insert("0.0", "⚠️ Couldn't read java file contents")

    def delete_profile(self):
        delete_profile(str(self.root.selected_profile))
        self.root.prof_list_ref.populate_profiles()
        self.root.selected_profile = None
        self.deactivate_buttons()

    def deactivate_buttons(self):
        for button in self.root.prof_butt_ref:
            button.configure(state="disabled")
