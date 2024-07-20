import builtins
import time
import os

import tkinter as tk

import customtkinter as ctk

from importlib.metadata import version

from PIL import Image
from appium.options.android import UiAutomator2Options

from test2va.bridge import check_file_exists, save_profile, get_profiles, \
    delete_profile, new_start_server, get_capability_options, parse, wait_app_load, mutate
from test2va.bridge.tool import generate
from test2va.gui.root.windows.cap_window.input.cap_entry.CTkScrollableDropdown import CTkScrollableDropdown
from test2va.gui.root import RootWidget
from test2va.gui.legacy.util import find_running_device, browse, java_browse, check_type_val, CallbackThread

menu_bg = "grey15"
menu_hover = "grey20"
menu_entry_height = 25
menu_entry_width = 200

home_entry_button_size = 15
home_entry_button_padx = 2

menu_icon_size = (20, 20)
asset_path = os.path.join(os.path.dirname(__file__), "assets")

java_entry_pad = 7
java_entry_radius = 10
java_entry_width = 300

other_input_pad_y = 5
other_entry_label_padx = 5

capability_frame_height = 185
max_rows_per_column = 4

cur_tab_color = "#1f538d"

prof_scrol_f_height = 415
prof_bg = "grey17"
prof_name_font = ("Roboto", 30)

output_box_height = 430


class GUI:
    def __init__(self):
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("dark-blue")

        self.cap_win_open = False
        self.sav_prof_win_open = False
        self.caps = get_capability_options()
        self.x_icon = ctk.CTkImage(Image.open(os.path.join(asset_path, "openmoji-x.png")).resize(menu_icon_size))
        self.cap_cache = {}
        self.loaded_profile = None
        self.selected_profile = None
        self.og_print = builtins.print
        self.temp_java = None
        self.driver = None
        self.app_service = None
        self.stop = False

        builtins.print = self.gui_print

        self.root = RootWidget()

        # Left Frame -------

        self.left_frame = ctk.CTkFrame(self.root, fg_color=menu_bg, corner_radius=0, border_width=0)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_rowconfigure(3, weight=1)

        self.home_icon = ctk.CTkImage(Image.open(os.path.join(asset_path, "openmoji-home.png")).resize(menu_icon_size))
        self.bust_icon = ctk.CTkImage(Image.open(os.path.join(asset_path, "openmoji-bust.png")).resize(menu_icon_size))
        self.play_icon = ctk.CTkImage(Image.open(os.path.join(asset_path, "openmoji-play.png")).resize(menu_icon_size))

        self.home_button = self.menu_entry("Home", self.home_tab_onclick, self.home_icon)
        self.prof_button = self.menu_entry("Profiles", self.prof_tab_onclick, self.bust_icon)
        self.run_button = self.menu_entry("Run", self.run_tab_onclick, self.play_icon)

        self.current_tab = self.home_button
        self.home_button.configure(fg_color=cur_tab_color, hover_color=cur_tab_color)

        # Right Frame -------

        self.right_frame = ctk.CTkFrame(self.root, corner_radius=0, border_width=0)
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=5)
        self.right_frame.grid_columnconfigure(1, weight=1)

        self.current_frame = self.right_frame

        # -- RF Home Input

        self.java_window = None

        self.home_input_frame = ctk.CTkFrame(self.right_frame, corner_radius=0, border_width=0)
        self.home_input_frame.grid(row=0, column=0, sticky="nsew")
        self.home_input_frame.grid_rowconfigure(4, weight=1)
        self.home_input_frame.grid_columnconfigure(0, weight=1)

        self.browse_icon = ctk.CTkImage(Image.open(os.path.join(asset_path, "openmoji-folder.png"))
                                        .resize(menu_icon_size))

        def bind():
            self.java_window_content = self.java_window.get("0.0", "end-1c")
            self.java_window.bind("<<Modified>>", self.java_text_change)

        def unbind():
            self.java_window.unbind("<<Modified>>")

        self.home_java_input, self.home_java_input_entry = self.home_entry(self.home_input_frame, "Java File",
                                                                           "Path to Java file",
                                                                           lambda f: java_browse(f, self.java_window,
                                                                                                 unbind, bind))
        self.home_apk_input, self.home_apk_entry = self.home_entry(self.home_input_frame, "APK File",
                                                                   "Path to app APK",
                                                                   lambda f: browse(f, [("APK files", "*.apk")]))
        devices = find_running_device()
        if devices:
            self.udid_input, self.udid_entry = self.home_entry(self.home_input_frame, "Device UDID", devices[0])
        else:
            self.udid_input, self.udid_entry = self.home_entry(self.home_input_frame, "Device UDID", "Device UDID")

        self.home_java_input.grid(row=0, column=0, sticky="new")
        self.home_apk_input.grid(row=1, column=0, sticky="new")
        self.udid_input.grid(row=2, column=0, sticky="new")

        # --- Capability Frame

        self.capability_frame = ctk.CTkFrame(self.home_input_frame, corner_radius=0, border_width=0,
                                             fg_color="transparent")
        self.capability_frame.grid(row=3, column=0, sticky="new", padx=java_entry_pad, pady=other_input_pad_y)
        self.capability_frame.grid_rowconfigure(0, weight=1)
        self.capability_frame.grid_rowconfigure(1, weight=0)
        self.capability_frame.grid_columnconfigure(0, weight=1)

        self.capability_add_frame = ctk.CTkFrame(self.capability_frame, corner_radius=0, border_width=0,
                                                 fg_color="transparent")
        self.capability_add_frame.grid(sticky="ew", row=0, column=0)
        self.capability_add_frame.grid_columnconfigure(0, weight=30)
        self.capability_add_frame.grid_columnconfigure(1, weight=1)
        #self.capability_frame.grid_rowconfigure(0, weight=1)

        self.capability_label = ctk.CTkLabel(self.capability_add_frame, text="Capabilities", corner_radius=0,
                                             anchor="w",
                                             justify="left")
        self.capability_label.grid(sticky="ew", row=0, column=0, padx=other_entry_label_padx)

        self.plus_icon = ctk.CTkImage(Image.open(os.path.join(asset_path, "openmoji-plus.png")).resize(menu_icon_size))
        self.capability_add_button = ctk.CTkButton(self.capability_add_frame, image=self.plus_icon, text="",
                                                   corner_radius=java_entry_radius, width=home_entry_button_size,
                                                   height=home_entry_button_size, command=self.capability_window)
        self.capability_add_button.grid(sticky="ew", row=0, column=1, padx=home_entry_button_padx)

        self.capability_scroll_frame = ctk.CTkScrollableFrame(self.capability_frame, corner_radius=java_entry_radius,
                                                              border_width=0, orientation="horizontal",
                                                              height=capability_frame_height)
        # self.capability_scroll_frame.columnconfigure(1, weight=1)
        self.capability_scroll_frame.grid(row=1, column=0, sticky="new")

        # --- Save Profile Button

        self.save_profile_button = ctk.CTkButton(self.home_input_frame, text="Save Profile",
                                                 command=self.save_prof_window)
        self.save_profile_button.grid(row=4, column=0, sticky="nsew", padx=java_entry_pad, pady=other_input_pad_y)

        # -- RF Java Window

        self.java_window_frame = ctk.CTkFrame(self.right_frame, corner_radius=0, border_width=0)
        self.java_window_frame.grid(row=0, column=1, sticky="nsew")
        self.java_window_frame.columnconfigure(0, weight=1)
        self.java_window_frame.rowconfigure(0, weight=1)

        self.java_window = ctk.CTkTextbox(self.java_window_frame, border_width=0, wrap="none", border_spacing=0,
                                          corner_radius=java_entry_radius, width=java_entry_width)
        self.java_window.insert("0.0", "Or paste Java source code")
        self.java_window.grid(sticky="nsew", padx=java_entry_pad, pady=java_entry_pad)

        self.java_window_content = self.java_window.get("0.0", "end-1c")
        self.java_window.bind("<<Modified>>", self.java_text_change)

        # - Profile Frame

        self.profile_frame = ctk.CTkFrame(self.root, corner_radius=0, border_width=0, fg_color=prof_bg)
        self.profile_frame.rowconfigure(1, weight=1)
        self.profile_frame.columnconfigure(0, weight=1)

        # -- Profile List Scroll Frame

        self.profile_scroll_frame = ctk.CTkScrollableFrame(self.profile_frame, corner_radius=java_entry_radius,
                                                           border_width=0, orientation="vertical",
                                                           height=prof_scrol_f_height)
        self.profile_scroll_frame.grid(row=0, column=0, sticky="nsew", padx=java_entry_pad, pady=5)
        self.profile_scroll_frame.columnconfigure(0, weight=1)

        self.populate_profiles()

        # -- Profile Action Frame

        self.profile_action_frame = ctk.CTkFrame(self.profile_frame, corner_radius=0, border_width=0,
                                                 fg_color="transparent")
        self.profile_action_frame.grid(row=1, column=0, sticky="sew", pady=5)
        self.profile_action_frame.columnconfigure(0, weight=4)
        self.profile_action_frame.columnconfigure(1, weight=1)
        self.profile_action_frame.rowconfigure(0, weight=1)

        # --- Profile Load Button

        self.load_profile_button = ctk.CTkButton(self.profile_action_frame, text="Load Profile", state="disabled",
                                                 command=self.load_profile)
        self.load_profile_button.grid(row=0, column=0, sticky="nsew", padx=java_entry_pad)

        # --- Profile Delete Button

        self.delete_profile_button = ctk.CTkButton(self.profile_action_frame, text="Delete Profile", state="disabled",
                                                   fg_color="red", command=self.delete_profile)
        self.delete_profile_button.grid(row=0, column=1, sticky="nsew", padx=java_entry_pad)

        # - Run Frame TODO: Resume refactor here

        self.run_frame = ctk.CTkFrame(self.root, corner_radius=0, border_width=0, fg_color=prof_bg)
        self.run_frame.rowconfigure(1, weight=1)
        self.run_frame.columnconfigure(0, weight=1)

        # -- Profile List Scroll Frame

        self.run_output_tb = ctk.CTkTextbox(self.run_frame, corner_radius=java_entry_radius, border_width=0,
                                            wrap="word", height=output_box_height)
        self.run_output_tb.grid(row=0, column=0, sticky="nsew", padx=java_entry_pad, pady=5)
        self.run_output_tb.insert("0.0", "Output will be displayed here")

        # -- Profile Action Frame

        self.run_tool_button = ctk.CTkButton(self.run_frame, text="Run Tool", command=self.run)
        self.run_tool_button.grid(row=1, column=0, sticky="sew", pady=5, padx=java_entry_pad)

        self.root.mainloop()

    def capability_window(self):
        if self.cap_win_open:
            return

        self.cap_win_open = True

        cap_pad_x = 8
        cap_pad_y = 3

        new_window = ctk.CTkToplevel(self.root)
        new_window.iconbitmap(os.path.join(os.path.dirname(__file__), "assets", "openmoji-android.ico"))
        new_window.geometry("500x200")
        new_window.resizable(False, False)
        new_window.protocol("WM_DELETE_WINDOW", lambda: self.cap_onclose(new_window))
        new_window.title(f"Test2VA Add New Capabilities")
        new_window.attributes("-topmost", True)

        new_window.rowconfigure(4, weight=1)
        new_window.columnconfigure(0, weight=1)

        # --- Cap Add Labels

        cap_add_frame = ctk.CTkFrame(new_window, corner_radius=0, border_width=0, fg_color="transparent")
        cap_add_frame.grid(row=0, column=0, sticky="new", pady=cap_pad_y)
        cap_add_frame.rowconfigure(0, weight=1)
        cap_add_frame.columnconfigure(0, weight=1)
        cap_add_frame.columnconfigure(1, weight=1)

        sel_cap_label = ctk.CTkLabel(cap_add_frame, text="Select Capability", corner_radius=0, anchor="w",
                                     justify="left")
        sel_cap_label.grid(row=0, column=0, sticky="nsew", padx=cap_pad_x)

        cap_val_label = ctk.CTkLabel(cap_add_frame, text="Capability Value", corner_radius=0, anchor="w",
                                     justify="left")
        cap_val_label.grid(row=0, column=1, sticky="nsew", padx=cap_pad_x)

        # --- Cap Desc Area

        cap_desc_area = ctk.CTkTextbox(new_window, corner_radius=java_entry_radius, border_width=0, wrap="word",
                                       height=70)
        cap_desc_area.grid(row=3, column=0, sticky="nsew", padx=cap_pad_x)
        cap_desc_area.insert("0.0", "Select a capability to view its description")

        # --- Cap Add Inputs

        cap_input_frame = ctk.CTkFrame(new_window, corner_radius=0, border_width=0, fg_color="transparent")
        cap_input_frame.grid(row=1, column=0, sticky="new")
        cap_input_frame.rowconfigure(0, weight=1)
        cap_input_frame.columnconfigure(0, weight=1)
        cap_input_frame.columnconfigure(1, weight=1)

        cap_entry_var = tk.StringVar()
        cap_entry = ctk.CTkEntry(cap_input_frame, corner_radius=java_entry_radius, textvariable=cap_entry_var)
        cap_entry.grid(row=0, column=1, sticky="nsew", padx=cap_pad_x)
        cap_entry.insert(0, "Integer")

        cap_combo_var = tk.StringVar()
        cap_combo_var.set("adb_exec_timeout")
        cap_combo = ctk.CTkComboBox(cap_input_frame)
        vals = [cap[0] for cap in self.caps]
        cap_combo.grid(row=0, column=0, sticky="nsew", padx=cap_pad_x)
        CTkScrollableDropdown(cap_combo, values=vals, corner_radius=java_entry_radius, autocomplete=True,
                              width=235,
                              command=lambda choice: self.cap_onselect(cap_combo, choice, cap_desc_area, cap_entry,
                                                                       cap_combo_var),
                              )

        # --- Cap Desc Label

        cap_desc_label = ctk.CTkLabel(new_window, text="Description", corner_radius=0, anchor="w", justify="left",
                                      fg_color="transparent")
        cap_desc_label.grid(row=2, column=0, sticky="new", padx=cap_pad_x)

        # --- Cap Buttons

        cap_button_frame = ctk.CTkFrame(new_window, corner_radius=0, border_width=0, fg_color="transparent")
        cap_button_frame.grid(row=4, column=0, sticky="sew", pady=cap_pad_y)
        cap_button_frame.rowconfigure(0, weight=1)
        cap_button_frame.columnconfigure(0, weight=6)
        cap_button_frame.columnconfigure(1, weight=1)

        cap_add_button = ctk.CTkButton(cap_button_frame, text="Add Capability", corner_radius=java_entry_radius,
                                       command=lambda: self.add_cap_to_main(cap_combo_var, cap_entry_var))
        cap_add_button.grid(row=0, column=0, sticky="nsew", padx=cap_pad_x)

        cap_cancel_button = ctk.CTkButton(cap_button_frame, text="Done", corner_radius=java_entry_radius,
                                          command=lambda: self.cap_onclose(new_window))
        cap_cancel_button.grid(row=0, column=1, sticky="nsew", padx=cap_pad_x)

    def save_prof_window(self):
        if self.sav_prof_win_open:
            return

        self.sav_prof_win_open = True

        new_window = ctk.CTkToplevel(self.root)
        new_window.iconbitmap(os.path.join(os.path.dirname(__file__), "assets", "openmoji-android.ico"))
        new_window.geometry("400x115")
        new_window.resizable(False, False)
        new_window.protocol("WM_DELETE_WINDOW", lambda: self.save_prof_onclose(new_window))
        new_window.title(f"Test2VA Save Profile")
        new_window.attributes("-topmost", True)

        new_window.rowconfigure(2, weight=1)
        new_window.columnconfigure(0, weight=1)

        # --- Save Profile Label

        save_prof_label = ctk.CTkLabel(new_window, text="Enter profile name", corner_radius=0, anchor="w",
                                       justify="left")
        save_prof_label.grid(row=0, column=0, sticky="nsew", padx=java_entry_pad, pady=5)

        # --- Save Profile Entry

        save_prof_entry_var = ctk.StringVar()
        save_prof_entry = ctk.CTkEntry(new_window, corner_radius=java_entry_radius, textvariable=save_prof_entry_var)
        save_prof_entry.grid(row=1, column=0, sticky="nsew", padx=5)

        if self.loaded_profile:
            save_prof_entry.insert(0, self.loaded_profile)

        # --- Save Profile Action Button Frame

        save_prof_button_frame = ctk.CTkFrame(new_window, corner_radius=0, border_width=0, fg_color="transparent")
        save_prof_button_frame.grid(row=2, column=0, sticky="sew", pady=5)
        save_prof_button_frame.rowconfigure(0, weight=1)
        save_prof_button_frame.columnconfigure(0, weight=6)
        save_prof_button_frame.columnconfigure(1, weight=1)

        save_prof_button = ctk.CTkButton(save_prof_button_frame, text="Save Profile", corner_radius=java_entry_radius,
                                         command=lambda: self.save_profile(save_prof_entry_var, save_prof_label))
        save_prof_button.grid(row=0, column=0, sticky="nsew", padx=5)

        cancel_button = ctk.CTkButton(save_prof_button_frame, text="Done", corner_radius=java_entry_radius,
                                      command=lambda: self.save_prof_onclose(new_window))
        cancel_button.grid(row=0, column=1, sticky="nsew", padx=5)

    def save_prof_onclose(self, win):
        self.sav_prof_win_open = False
        win.destroy()

    def save_profile(self, name, label):
        # Return if name is empty
        if not name.get():
            label.configure(text="⚠️ Please enter a profile name")
            return

        if self.home_java_input_entry.get() and self.home_java_input_entry.get() != "Path to Java file":
            if not check_file_exists(self.home_java_input_entry.get()):
                label.configure(text="⚠️ Please enter a valid Java file path")
                return
            j_path = self.home_java_input_entry.get()
            j_code = None
        elif self.java_window_content != "Or paste Java source code":
            j_path = None
            j_code = self.java_window_content
        else:
            label.configure(text="⚠️ Please enter a Java file path or paste Java source code")
            return

        if not check_file_exists(self.home_apk_entry.get()):
            label.configure(text="⚠️ Please enter a valid APK file path")
            return

        if not self.udid_entry.get() or self.udid_entry.get() == "Device UDID":
            label.configure(text="⚠️ Please enter a valid device UDID")
            return

        caps = {}
        for cap, val in self.cap_cache.items():
            cap_type = self.get_cap_type(cap)
            if cap_type == "bool":
                caps[cap] = val.lower() == "true"
            elif cap_type == "int":
                caps[cap] = int(val)
            else:
                caps[cap] = val

        save_profile(name.get(), self.home_apk_entry.get(), caps, self.udid_entry.get(), j_path, j_code)

        self.populate_profiles()

        label.configure(text="✔️ Profile saved successfully")

    def cap_onclose(self, win):
        self.cap_win_open = False
        win.destroy()

    def cap_onselect(self, combo, choice, desc, entry, var):
        for cap in self.caps:
            if cap[0] == choice:
                var.set(choice)
                combo.set(choice)
                desc.delete("0.0", "end")
                desc.insert("0.0", cap[2])
                entry.delete(0, tk.END)
                if cap[1] == "bool":
                    entry.insert(0, "Boolean")
                elif cap[1] == "int":
                    entry.insert(0, "Integer")
                else:
                    entry.insert(0, "String")
                break

    def add_cap_to_main(self, cap, val):
        if cap.get() in self.cap_cache:
            return

        check = check_type_val(self.get_cap_type(cap.get()), val.get())
        if not check:
            return

        entry = self.make_cap_entry(self.capability_scroll_frame, cap.get(), val.get())
        col = len(self.cap_cache) // max_rows_per_column
        row = len(self.cap_cache) % max_rows_per_column
        entry.grid(row=row, column=col, padx=5, pady=5, sticky="w")

        self.cap_cache[cap.get()] = val.get()

    def make_cap_entry(self, parent, cap, val):
        cap_frame = ctk.CTkFrame(parent, corner_radius=java_entry_radius, border_width=0, fg_color=menu_hover)
        cap_frame.rowconfigure(0, weight=1)
        cap_frame.columnconfigure(1, weight=1)

        cap_label = ctk.CTkLabel(cap_frame, text=f"{cap}: {val}", corner_radius=0, anchor="w", justify="left",
                                 fg_color="transparent")
        cap_label.grid(row=0, column=0, sticky="nsew", padx=4, pady=2)

        cap_button = ctk.CTkButton(cap_frame, text="", image=self.x_icon, width=10, hover_color=menu_hover,
                                   height=10, fg_color="transparent", corner_radius=0,
                                   command=lambda: self.remove_cap(cap))
        cap_button.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)

        return cap_frame

    def onclose(self):
        self.root.destroy()

    def remove_cap(self, cap):
        self.cap_cache.pop(cap)
        self.redraw_caps()

    def redraw_caps(self):
        # Remove all items from the scrollable frame
        for widget in self.capability_scroll_frame.winfo_children():
            widget.destroy()

        col = 0
        row = 0

        for cap, val in self.cap_cache.items():
            frame = self.make_cap_entry(self.capability_scroll_frame, cap, val)
            frame.grid(row=row, column=col, padx=5, pady=5, sticky="w")

            row += 1
            if row >= max_rows_per_column:
                row = 0
                col += 1

    def make_profile_entry(self, parent, name, java, apk, udid, caps):
        p_frame = ctk.CTkFrame(parent, corner_radius=java_entry_radius, fg_color=prof_bg)
        p_frame.columnconfigure(0, weight=1)
        p_frame.columnconfigure(1, weight=1)
        p_frame.rowconfigure(0, weight=1)

        # Large font
        name_label = ctk.CTkLabel(p_frame, text=name, corner_radius=0, anchor="w", justify="left",
                                  fg_color="transparent", font=prof_name_font)
        name_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        other_info_frame = ctk.CTkFrame(p_frame, corner_radius=0, border_width=0, fg_color="transparent")
        other_info_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        other_info_frame.rowconfigure(0, weight=1)
        other_info_frame.rowconfigure(1, weight=1)
        other_info_frame.rowconfigure(2, weight=1)
        other_info_frame.rowconfigure(3, weight=1)
        other_info_frame.columnconfigure(0, weight=1)

        j_file_name = os.path.basename(java)
        if j_file_name == "java_src_code.java":
            j_file_name = "Pasted Java Code"

        java_label = ctk.CTkLabel(other_info_frame, text=j_file_name, corner_radius=0, anchor="e",
                                  justify="right", fg_color="transparent")
        java_label.grid(row=0, column=0, sticky="nsew")

        apk_label = ctk.CTkLabel(other_info_frame, text=os.path.basename(apk), corner_radius=0, anchor="e",
                                 justify="right", fg_color="transparent")
        apk_label.grid(row=1, column=0, sticky="nsew")

        udid_label = ctk.CTkLabel(other_info_frame, text=udid, corner_radius=0, anchor="e",
                                  justify="right", fg_color="transparent")
        udid_label.grid(row=2, column=0, sticky="nsew")

        cap_label = ctk.CTkLabel(other_info_frame, text=f"Capabilties: {len(caps)}", corner_radius=0, anchor="e",
                                 justify="right", fg_color="transparent")
        cap_label.grid(row=3, column=0, sticky="nsew")

        # p_frame on hover event
        def on_enter(_event):
            if p_frame.cget("fg_color") == cur_tab_color:
                return

            p_frame.configure(fg_color=menu_hover)

        def on_leave(_event):
            if p_frame.cget("fg_color") == cur_tab_color:
                return

            p_frame.configure(fg_color=prof_bg)

        def on_click(_event):
            self.load_profile_button.configure(state="normal")
            self.delete_profile_button.configure(state="normal")
            self.selected_profile = name

            for child in parent.winfo_children():
                child.configure(fg_color=prof_bg)

            p_frame.configure(fg_color=cur_tab_color)

        def bind_hover_events(widget):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)
            for child in widget.winfo_children():
                bind_hover_events(child)

        # Bind the hover events to the parent frame and all its descendants
        bind_hover_events(p_frame)

        return p_frame

    def populate_profiles(self):
        for widget in self.profile_scroll_frame.winfo_children():
            widget.destroy()

        profiles = get_profiles()
        for prof in profiles:
            p = self.make_profile_entry(self.profile_scroll_frame, prof["name"], prof["java_path"], prof["apk"],
                                        prof["udid"], prof["caps"])
            p.grid(sticky="new", padx=5, pady=5)

        if len(profiles) <= 0:
            no_prof_label = ctk.CTkLabel(self.profile_scroll_frame, text="No profiles saved", corner_radius=0,
                                         anchor="center", justify="center", fg_color="transparent")
            no_prof_label.grid(sticky="new", padx=5, pady=5)

    def load_profile(self):
        profiles = get_profiles()
        for prof in profiles:
            if prof["name"] == self.selected_profile:
                self.loaded_profile = self.selected_profile
                self.home_java_input_entry.delete(0, tk.END)
                self.home_java_input_entry.insert(0, prof["java_path"])
                self.home_java_input_entry.xview(tk.END)
                self.home_apk_entry.delete(0, tk.END)
                self.home_apk_entry.insert(0, prof["apk"])
                self.home_apk_entry.xview(tk.END)
                self.udid_entry.delete(0, tk.END)
                self.udid_entry.insert(0, prof["udid"])
                self.cap_cache = {cap: str(val) for cap, val in prof["caps"].items()}
                self.redraw_caps()

                try:
                    # Read the java path and display its contents
                    with open(prof["java_path"], "r") as f:
                        self.java_window.delete("0.0", "end")
                        self.java_window.insert("0.0", f.read())
                        self.java_window_content = self.java_window.get("0.0", "end-1c")
                except Exception:
                    self.java_window.delete("0.0", "end")
                    self.java_window.insert("0.0", "⚠️ Couldn't read java file contents")

                break

    def delete_profile(self):
        delete_profile(self.selected_profile)
        self.populate_profiles()
        self.selected_profile = None

    def get_cap_type(self, cap):
        for c in self.caps:
            if c[0] == cap:
                return c[1]

    def populate_capabilities(self):
        self.caps = get_capability_options()

    def change_tab(self, tab):
        self.current_tab.configure(fg_color=menu_bg, hover_color=menu_hover)
        tab.configure(fg_color=cur_tab_color, hover_color=cur_tab_color)
        self.current_tab = tab

    def home_tab_onclick(self):
        if self.current_tab == self.home_button:
            return

        self.change_tab(self.home_button)
        self.current_frame.grid_forget()
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        self.current_frame = self.right_frame

    def prof_tab_onclick(self):
        if self.current_tab == self.prof_button:
            return

        self.change_tab(self.prof_button)
        self.current_frame.grid_forget()
        self.profile_frame.grid(row=0, column=1, sticky="nsew")
        self.current_frame = self.profile_frame

    def run_tab_onclick(self):
        if self.current_tab == self.run_button:
            return

        self.change_tab(self.run_button)
        self.current_frame.grid_forget()
        self.run_frame.grid(row=0, column=1, sticky="nsew")
        self.current_frame = self.run_frame

    def java_text_change(self, _event):
        new_content = self.java_window.get("0.0", "end-1c")
        if new_content == self.java_window_content:
            self.java_window.edit_modified(False)
            return

        self.home_java_input_entry.delete(0, tk.END)
        self.java_window_content = new_content
        self.java_window.edit_modified(False)

    def menu_entry(self, text, command, img):
        entry = ctk.CTkButton(self.left_frame, text=text, command=command, corner_radius=0, height=menu_entry_height,
                              border_spacing=10, anchor="w", fg_color=menu_bg, hover_color=menu_hover, image=img,
                              width=menu_entry_width)
        entry.grid(sticky="ew")

        return entry

    def home_entry(self, parent, label_text, entry_text, browse_command=None):
        # ---- Entry frame
        entry_input_frame = ctk.CTkFrame(parent, corner_radius=0, border_width=0, fg_color="transparent")
        entry_input_frame.grid(row=0, column=0, sticky="new", padx=java_entry_pad, pady=other_input_pad_y)
        entry_input_frame.grid_rowconfigure(1, weight=1)
        entry_input_frame.grid_columnconfigure(0, weight=20)
        entry_input_frame.grid_columnconfigure(1, weight=1)

        # ------ Entry input label

        entry_input_label = ctk.CTkLabel(entry_input_frame, text=label_text, corner_radius=0, anchor="w",
                                         justify="left")
        entry_input_label.grid(sticky="ew", row=0, column=0, padx=other_entry_label_padx)

        # ------ Entry input

        entry_input = ctk.CTkEntry(entry_input_frame, corner_radius=java_entry_radius)
        entry_input.insert(0, entry_text)

        if browse_command is not None:
            entry_input.grid(sticky="ew", row=1, column=0)
        else:
            entry_input.grid(sticky="ew", row=1, column=0, columnspan=2)

        # ------ Java path browse button

        if browse_command is not None:
            entry_input_browse = ctk.CTkButton(entry_input_frame, image=self.browse_icon, text="",
                                               corner_radius=java_entry_radius, width=home_entry_button_size,
                                               height=home_entry_button_size,
                                               command=lambda: browse_command(entry_input))
            entry_input_browse.grid(sticky="ew", row=1, column=1, padx=home_entry_button_padx)

        return entry_input_frame, entry_input

    def gui_print(self, *args, **kwargs):
        self.og_print(*args, **kwargs)
        args = [str(arg) for arg in args]
        self.run_output_tb.insert("end", f"{' '.join(args)}\n")

    def gui_stop(self, *args, **kwargs):
        self.stop = True
        print("ℹ️ Stop Request Received...")
        self.root.title(f"Test2VA {version('test2va')} - Waiting to stop...")

    def check_stop(self):
        if self.stop:
            self.stop = False
            raise Exception("Stopped by user")

    def run(self):
        self.run_output_tb.delete("0.0", "end")

        if self.home_java_input_entry.get() and self.home_java_input_entry.get() != "Path to Java file":
            if not check_file_exists(self.home_java_input_entry.get(), print):
                print("⚠️ Please enter a valid Java file path")
                return
            j_path = self.home_java_input_entry.get()
            j_code = None
        elif self.java_window_content != "Or paste Java source code":
            j_path = None
            j_code = self.java_window_content
        else:
            print("⚠️ Please enter a Java file path or paste Java source code")
            return

        if not check_file_exists(self.home_apk_entry.get(), print):
            print("⚠️ Please enter a valid APK file path")
            return

        if not self.udid_entry.get() or self.udid_entry.get() == "Device UDID":
            print("⚠️ Please enter a valid device UDID")
            return

        if j_code is not None:
            # Create a temp file to store the java code
            self.temp_java = os.path.join(os.path.dirname(__file__), "../temp_java.java")
            with open(self.temp_java, "w") as f:
                f.write(j_code)

            j_path = self.temp_java

        caps = {}
        for cap, val in self.cap_cache.items():
            cap_type = self.get_cap_type(cap)
            if cap_type == "bool":
                caps[cap] = val.lower() == "true"
            elif cap_type == "int":
                caps[cap] = int(val)
            else:
                caps[cap] = val

        options = UiAutomator2Options()
        options.udid = self.udid_entry.get()
        options.app = self.home_apk_entry.get()
        options.automation_name = "UiAutomator2"

        for cap, val in caps.items():
            try:
                setattr(options, cap, val)
            except Exception as e:
                print(str(e))
                print(f"⚠️ Capability {cap} could not be set to {val}")
                return

        def thread_func(*args, **kwargs):
            try:
                self.run_tool_button.configure(text="Stop Tool", fg_color="red", command=self.gui_stop)

                self.root.title(f"Test2VA {version('test2va')} - Starting Appium Server...")
                self.driver, self.app_service = new_start_server(options, print, self.gui_stop)
                self.check_stop()

                start = time.time()
                data, output_path = parse(self.home_apk_entry.get(), j_path, self.driver, print, self.gui_stop)
                self.check_stop()

                self.root.title(f"Test2VA {version('test2va')} - Waiting for app to load...")
                wait_app_load(print)

                self.root.title(f"Test2VA {version('test2va')} - Attempting possible mutable paths...")
                mutate(self.driver, data, start, output_path, print, self.gui_stop)
                self.check_stop()

                generate(self.driver, output_path, print, self.gui_stop)
                self.check_stop()

                return
            except Exception as e:
                print(str(e))
                return

        def thread_finished(*args, **kwargs):
            self.root.title(f"Test2VA {version('test2va')}")
            self.run_tool_button.configure(text="Run Tool", fg_color=cur_tab_color, command=self.run)

            if self.driver is not None and self.driver.session_id is not None:
                try:
                    self.app_service.stop()
                except Exception:
                    pass
                try:
                    print("ℹ️ Stopping Appium Server...")
                    self.driver.quit()
                    print("ℹ️ Appium Server Stopped")
                    self.driver = None
                except Exception:
                    self.driver = None

        thread = CallbackThread(target=thread_func, callback=thread_finished)
        thread.start()
