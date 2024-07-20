import customtkinter as ctk
import tkinter as tk

from test2va.gui.shared import gen_corner_rad, def_jsrc_entry

border_width = 0
wrap = "none"
border_spacing = 0
corner_rad = gen_corner_rad
width = 300

def_text = def_jsrc_entry


class JavaTextboxWidget(ctk.CTkTextbox):
    def __init__(self, parent):
        super().__init__(parent, wrap=wrap, corner_radius=corner_rad, border_width=border_width, width=width,
                         border_spacing=border_spacing)

        self.root = self.winfo_toplevel()
        self.insert("0.0", def_text)

        self.root.java_window_content = self.get("0.0", "end-1c")
        self.bind("<<Modified>>", self.on_modified)

    def on_modified(self, _event):
        new_content = self.get("0.0", "end-1c")
        if new_content == self.root.java_window_content:
            self.edit_modified(False)
            return

        self.root.java_path_ref.delete(0, tk.END)
        self.root.java_window_content = new_content
        self.edit_modified(False)