import customtkinter as ctk

from test2va.bridge import check_file_exists, save_profile
from test2va.gui.root.windows.save_window.button_frame.button import SaveProfButtonWidget
from test2va.gui.shared import def_java_entry, def_udid_entry

corner_rad = 0
border_width = 0
fg = "transparent"

cols = [6, 1]
rows = [1]

button_row = 0
sticky = "nsew"
padx = 5

save_col = 0
done_col = 1


class SaveProfButtonFrameWidget(ctk.CTkFrame):
    def __init__(self, parent, entry, label):
        super().__init__(parent, corner_radius=corner_rad, border_width=border_width, fg_color=fg)

        self.root = self.winfo_toplevel().root
        self.entry = entry
        self.label = label

        for i in range(len(rows)):
            self.grid_rowconfigure(i, weight=rows[i])

        for i in range(len(cols)):
            self.grid_columnconfigure(i, weight=cols[i])

        self.save = SaveProfButtonWidget(self, text="Save Profile", command=self.save_profile)
        self.save.grid(row=button_row, column=save_col, sticky=sticky, padx=padx)

        self.done = SaveProfButtonWidget(self, text="Done", command=self.done)
        self.done.grid(row=button_row, column=done_col, sticky=sticky, padx=padx)

    def save_profile(self):
        if not self.entry.get():
            self.label.configure(text="⚠️ Please enter a profile name")
            return

        i_frame = self.root.i_frame_ref

        if i_frame.java_entry.input.get() and i_frame.java_entry.input.get() != def_java_entry:
            if not check_file_exists(i_frame.java_entry.input.get()):
                self.label.configure(text="⚠️ Please enter a valid Java file path")
                return
            j_path = i_frame.java_entry.input.get()
            j_code = None
        elif self.root.java_window_content != "Or paste Java source code":
            j_path = None
            j_code = self.root.java_window_content
        else:
            self.label.configure(text="⚠️ Please enter a Java file path or paste Java source code")
            return

        if not check_file_exists(i_frame.apk_entry.input.get()):
            self.label.configure(text="⚠️ Please enter a valid APK file path")
            return

        if not i_frame.udid_entry.input.get() or i_frame.udid_entry.input.get() == def_udid_entry:
            self.label.configure(text="⚠️ Please enter a valid device UDID")
            return

        caps = self.root.format_caps()

        save_profile(self.entry.get(), i_frame.apk_entry.input.get(), caps, i_frame.udid_entry.input.get(), j_path,
                     j_code)

        self.root.prof_list_ref.populate_profiles()

        self.label.configure(text="✔️ Profile saved successfully")

    def done(self):
        self.root.sav_prof_open = False
        self.winfo_toplevel().destroy()
