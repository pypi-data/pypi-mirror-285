import customtkinter as ctk

from test2va.gui.root.windows.cap_window.button_frame.button import CapAddWinButtonWidget
from test2va.gui.shared import cap_padx

corner_rad = 0
border_width = 0
fg = "transparent"

cols = [6, 1]
rows = [1]

add_text = "Add Capability"
add_col = 0
add_row = 0

done_text = "Done"
done_col = 1
done_row = 0

sticky = "nsew"
padx = cap_padx


class CapAddButtonFrameWidget(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=corner_rad, border_width=border_width, fg_color=fg)

        for i in range(len(rows)):
            self.grid_rowconfigure(i, weight=rows[i])

        for i in range(len(cols)):
            self.grid_columnconfigure(i, weight=cols[i])

        self.root = self.winfo_toplevel().root

        self.add = CapAddWinButtonWidget(self, text=add_text, command=self.add_cap)
        self.add.grid(row=add_row, column=add_col, sticky=sticky, padx=padx)

        self.done = CapAddWinButtonWidget(self, text=done_text, command=self.done)
        self.done.grid(row=done_row, column=done_col, sticky=sticky, padx=padx)

    def add_cap(self):
        cap = self.root.cap_ref.combo.get()
        val = self.root.cap_val_ref.get()

        if cap in self.root.cap_cache:
            return

        cap_type = self.root.get_cap_type(cap)
        if not check_type_val(cap_type, val):
            return

        self.root.cap_cache[cap] = val
        self.root.cap_frame_ref.redraw_caps()

    def done(self):
        self.root.cap_window_open = False
        self.winfo_toplevel().destroy()


def check_type_val(typee: str, val: str):
    if typee == "str":
        return True
    elif typee == "int":
        try:
            int(val)
            return True
        except ValueError:
            return False
    elif typee == "bool":
        return val.lower() == "true" or val.lower() == "false"
