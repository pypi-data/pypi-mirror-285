import customtkinter as ctk
import tkinter as tk

from test2va.gui.root.windows.cap_window.input.cap_entry.CTkScrollableDropdown import CTkScrollableDropdown
from test2va.gui.shared import gen_corner_rad, cap_padx

corner_rad = gen_corner_rad
autocomplete = True
width = 235

cap_col = 0
cap_row = 0
sticky = "nsew"
padx = cap_padx


class NewCapInputCapWidget:
    def __init__(self, parent):
        self.combo = ctk.CTkComboBox(parent)
        self.root = self.combo.winfo_toplevel().root
        self.values = [cap[0] for cap in self.root.caps]

        self.combo.grid(row=cap_row, column=cap_col, sticky=sticky, padx=padx)

        CTkScrollableDropdown(self.combo, values=self.values, width=width, autocomplete=autocomplete,
                              corner_radius=corner_rad, command=lambda choice: self.on_select(choice))

    def on_select(self, choice):
        cap_desc = self.root.cap_desc_ref
        cap_val = self.root.cap_val_ref

        for cap in self.root.caps:
            if cap[0] == choice:
                self.combo.set(choice)

                cap_desc.delete("0.0", tk.END)
                cap_desc.insert("0.0", cap[2])

                cap_val.delete(0, tk.END)

                if cap[1] == "bool":
                    cap_val.insert(0, "Boolean")
                elif cap[1] == "int":
                    cap_val.insert(0, "Integer")
                else:
                    cap_val.insert(0, "String")
                break
