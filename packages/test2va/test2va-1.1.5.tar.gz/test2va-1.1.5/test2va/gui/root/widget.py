import os
import threading

import customtkinter as ctk

from test2va.bridge import get_capability_options, get_cap_type, format_caps, check_file_exists
from test2va.execute import ToolExec
from test2va.gui.root.tabs import TabFrameWidget
from importlib.metadata import version

from test2va.gui.shared import def_udid_entry, def_jsrc_entry

size_x = 900
size_y = 480

resize_x = False
resize_y = False

title = f"Test2VA {version('test2va')}"
icon = os.path.join(os.path.dirname(__file__), "./assets", "openmoji-android.ico")

columns = 1
c_weight = 1

tab_col = 0
page_col = 1

rows = 0
r_weight = 1

frame_grid = "nsew"


class RootWidget(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.java_window_content = ""

        self.cap_window_open = False
        self.sav_prof_open = False

        # Main Refs
        self.java_path_ref = None
        self.java_src_ref = None
        self.cap_frame_ref = None
        self.i_frame_ref = None
        self.prof_list_ref = None
        self.prof_butt_ref = None
        self.stat_prev_ref = None
        self.stat_guide_ref = None
        self.stat_list_ref = None
        self.run_out_ref = None
        self.run_butt_ref = None

        # Cap Add Refs
        self.cap_desc_ref = None
        self.cap_val_ref = None
        self.cap_ref = None

        self.selected_profile = None
        self.loaded_profile = None

        self.cur_tab = None
        self.cur_page = None

        self.cap_cache = {}
        self.page_cache = {}

        self.Exe = None

        self.caps = get_capability_options()

        self.geometry(f"{size_x}x{size_y}")
        self.resizable(resize_x, resize_y)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.title(title)
        self.iconbitmap(icon)

        self.grid_columnconfigure(columns, weight=c_weight)
        self.grid_rowconfigure(rows, weight=r_weight)

        self.tab_frame = TabFrameWidget(self)
        self.tab_frame.grid(row=0, column=tab_col, sticky=frame_grid)

        # Note: Home page does not need to be initialized here,
        # it is set as the default tab in the TabFrameWidget class

    def get_cap_type(self, cap):
        return get_cap_type(self.caps, cap)

    def format_caps(self):
        return format_caps(self.cap_cache, self.caps)

    def on_closing(self):
        self.quit()
        self.destroy()

    def stop(self):
        if self.Exe is None or self.Exe.stopped:
            return

        self.Exe.stop()
        self.run_butt_ref.configure(text="Stopping...", state="disabled")

    def run(self):
        self._on_start()

        apk = self.i_frame_ref.apk_entry.input.get()
        udid = self.i_frame_ref.udid_entry.input.get()

        if self.i_frame_ref.java_entry.input.get() and self.i_frame_ref.java_entry.input.get() != "Path to Java file":
            if not check_file_exists(self.i_frame_ref.java_entry.input.get(), print):
                self._on_error("Please enter a valid Java file path")
                return
            j_path = self.i_frame_ref.java_entry.input.get()
            j_code = None
        elif self.java_window_content != def_jsrc_entry:
            j_path = None
            j_code = self.java_window_content
        else:
            self._on_error("Please enter a Java file path or paste Java source code", "")
            return

        if not check_file_exists(apk, print):
            self._on_error("Please enter a valid APK file path", "")
            return

        if not udid or udid == def_udid_entry:
            self._on_error("Please enter a valid device UDID", "")
            return

        Exe = ToolExec(udid=udid, apk=apk, added_caps=self.cap_cache, cap_data=self.caps, j_path=j_path, j_code=j_code)
        Exe.events.on_start.connect(self._on_start)
        Exe.events.on_error.connect(self._on_error)
        Exe.events.on_log.connect(self._on_log)
        Exe.events.on_progress.connect(self._on_progress)
        Exe.events.on_success.connect(self._on_success)
        Exe.events.on_finish.connect(self._on_finish)

        self.Exe = Exe

        threading.Thread(target=Exe.execute).start()

    def _on_start(self):
        self.run_out_ref.delete("0.0", "end")

    def _on_error(self, msg, _err):
        self.run_out_ref.insert("end", f"❌ {msg}\n")

    def _on_log(self, msg):
        self.run_out_ref.insert("end", f"ℹ️ {msg}\n")
        print(f"ℹ️{msg}")

    def _on_progress(self, msg):
        self.title(f"Test2VA {version('test2va')} - {msg}...")
        self.run_out_ref.insert("end", f"ℹ️ {msg}\n")

    def _on_success(self, msg):
        self.title(f"Test2VA {version('test2va')}")
        self.run_out_ref.insert("end", f"✅ {msg}\n")

    def _on_finish(self):
        self.title(f"Test2VA {version('test2va')}")
        self.run_out_ref.insert("end", "🛑 Execution Stopped\n")

        if self.stat_list_ref is not None:
            self.stat_list_ref.redraw_stats()

        self.run_butt_ref.reset()
