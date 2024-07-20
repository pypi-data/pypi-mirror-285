import os
import threading
import time

import tkinter as tk


from appium.options.android.uiautomator2.base import UiAutomator2Options

from test2va.bridge import list_examples, get_example_data, check_file_exists
from test2va.bridge.appium import new_start_server
from test2va.gui.components import title_bar
from test2va.gui.legacy.util import browse
from test2va.mutator import mutator
from test2va.parser import parser
from test2va.generator import generator
from test2va.util.write_json import write_json


class OldGUI:
    def __init__(self):
        self.options = None
        self.output_text = ""
        self.driver = None
        self.started = False

        self.root = tk.Tk()
        self.root.title("Test2VA")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # self.root.overrideredirect(True)

        self.root.protocol("WM_DELETE_WINDOW", self.onclose)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.main_frame = tk.Frame(self.root, highlightthickness=0)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=0)
        self.main_frame.grid_rowconfigure(1, weight=30)
        self.main_frame.grid_rowconfigure(2, weight=70)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.title_bar = title_bar(self)
        # self.title_bar.grid(row=0, column=0, sticky="nsew")

        self.top_portion = tk.Frame(self.main_frame, bg="red")
        self.top_portion.grid(row=1, column=0, sticky="nsew")
        self.top_portion.grid_columnconfigure(0, weight=1)
        self.top_portion.grid_rowconfigure(0, weight=1)
        self.top_portion.grid_rowconfigure(1, weight=1)
        self.top_portion.grid_rowconfigure(2, weight=1)
        self.top_portion.grid_rowconfigure(3, weight=1)

        self.app_input_frame = tk.Frame(self.top_portion)
        self.app_input_frame.grid(row=0, column=0, sticky="nsew")
        self.app_input_frame.grid_rowconfigure(0, weight=1)
        self.app_input_frame.grid_columnconfigure(0, weight=4)
        self.app_input_frame.grid_columnconfigure(1, weight=1)

        self.app_input_guide = tk.Frame(self.app_input_frame)
        self.app_input_guide.columnconfigure(0, weight=10)
        self.app_input_guide.rowconfigure(0, weight=10)
        self.app_input_guide.grid(row=0, column=0, sticky="nsew")
        self.app_input_guide.grid_propagate(False)

        self.app_input_text = tk.Entry(self.app_input_guide, textvariable=tk.StringVar())
        self.app_input_text.insert(0, "Enter file path to app apk")
        self.app_input_text.grid(sticky="ew")

        self.app_browse_guide = tk.Frame(self.app_input_frame)
        self.app_browse_guide.columnconfigure(0, weight=10)
        self.app_browse_guide.rowconfigure(0, weight=10)
        self.app_browse_guide.grid(row=0, column=1, sticky="nsew")
        self.app_browse_guide.grid_propagate(False)

        self.app_browse_button = tk.Button(self.app_browse_guide, text="Browse",
                                           command=lambda: browse(self.app_input_text))
        self.app_browse_button.grid(row=0, column=0, sticky="ew")

        self.java_input_frame = tk.Frame(self.top_portion, bg="orange")
        self.java_input_frame.grid(row=1, column=0, sticky="nsew")
        self.java_input_frame.grid_rowconfigure(0, weight=1)
        self.java_input_frame.grid_columnconfigure(0, weight=4)
        self.java_input_frame.grid_columnconfigure(1, weight=1)

        self.java_input_guide = tk.Frame(self.java_input_frame)
        self.java_input_guide.columnconfigure(0, weight=10)
        self.java_input_guide.rowconfigure(0, weight=10)
        self.java_input_guide.grid(row=0, column=0, sticky="nsew")
        self.java_input_guide.grid_propagate(False)

        self.java_input_text = tk.Entry(self.java_input_guide, textvariable=tk.StringVar())
        self.java_input_text.insert(0, "Enter file path to java file")
        self.java_input_text.grid(sticky="ew")

        self.java_browse_guide = tk.Frame(self.java_input_frame)
        self.java_browse_guide.columnconfigure(0, weight=10)
        self.java_browse_guide.rowconfigure(0, weight=10)
        self.java_browse_guide.grid(row=0, column=1, sticky="nsew")
        self.java_browse_guide.grid_propagate(False)

        self.java_browse_button = tk.Button(self.java_browse_guide, text="Browse",
                                            command=lambda: browse(self.java_input_text))
        self.java_browse_button.grid(row=0, column=0, sticky="ew")

        self.url_input_frame = tk.Frame(self.top_portion)
        self.url_input_frame.grid(row=2, column=0, sticky="nsew")
        self.url_input_frame.grid_rowconfigure(0, weight=1)
        self.url_input_frame.grid_columnconfigure(0, weight=1)

        self.url_input_guide = tk.Frame(self.url_input_frame)
        self.url_input_guide.columnconfigure(0, weight=10)
        self.url_input_guide.rowconfigure(0, weight=10)
        self.url_input_guide.grid(row=0, column=0, sticky="nsew")
        self.url_input_guide.grid_propagate(False)

        self.url_input_text = tk.Entry(self.url_input_guide, textvariable=tk.StringVar())
        self.url_input_text.insert(0, "Enter Appium server url")
        self.url_input_text.grid(sticky="ew")

        self.example_input_frame_guide = tk.Frame(self.top_portion)
        self.example_input_frame_guide.grid(row=3, column=0, sticky="nsew")
        self.example_input_frame_guide.grid_rowconfigure(0, weight=1)
        self.example_input_frame_guide.grid_columnconfigure(0, weight=1)

        options_list = ["Select an example"]
        examples = list_examples()
        for example in examples:
            options_list.append(example)

        self.dropdown_var = tk.StringVar()
        self.dropdown_var.set(options_list[0])
        self.dropdown_var.trace("w", self.ddtrace)
        self.example_dropdown = tk.OptionMenu(self.example_input_frame_guide, self.dropdown_var, *options_list)
        self.example_dropdown.grid(sticky="nsew")

        self.bottom_portion = tk.Frame(self.main_frame)
        self.bottom_portion.grid(row=2, column=0, sticky="nsew")
        self.bottom_portion.grid_rowconfigure(0, weight=1)
        self.bottom_portion.grid_columnconfigure(0, weight=1)
        self.bottom_portion.grid_columnconfigure(1, weight=4)

        self.capability_frame = tk.Frame(self.bottom_portion, bg="blue")
        self.capability_frame.grid(row=0, column=0, sticky="nsew")
        self.capability_frame.grid_columnconfigure(0, weight=1)
        self.capability_frame.grid_rowconfigure(0, weight=1)
        self.capability_frame.grid_rowconfigure(1, weight=1)
        self.capability_frame.grid_rowconfigure(2, weight=5)
        self.capability_frame.grid_rowconfigure(3, weight=2)

        self.udid_input_frame = tk.Frame(self.capability_frame, bg="yellow")
        self.udid_input_frame.grid(row=0, column=0, sticky="nsew")
        self.udid_input_frame.grid_columnconfigure(0, weight=1)
        self.udid_input_frame.grid_rowconfigure(0, weight=1)
        self.udid_input_frame.grid_rowconfigure(1, weight=1)

        self.udid_label = tk.Label(self.udid_input_frame, text="UDID", anchor="w")
        self.udid_label.grid(row=0, column=0, sticky="nsew")

        self.udid_input_guide = tk.Frame(self.udid_input_frame)
        self.udid_input_guide.columnconfigure(0, weight=10)
        self.udid_input_guide.rowconfigure(0, weight=10)
        self.udid_input_guide.grid(row=1, column=0, sticky="nsew")
        self.udid_input_guide.grid_propagate(False)

        self.udid_input_text = tk.Entry(self.udid_input_guide, textvariable=tk.StringVar())
        self.udid_input_text.grid(sticky="nsew")

        self.activity_input_frame = tk.Frame(self.capability_frame, bg="purple")
        self.activity_input_frame.grid(row=1, column=0, sticky="nsew")
        self.activity_input_frame.grid_columnconfigure(0, weight=1)
        self.activity_input_frame.grid_rowconfigure(0, weight=1)
        self.activity_input_frame.grid_rowconfigure(1, weight=1)

        self.activity_label = tk.Label(self.activity_input_frame, text="App Wait Activity", anchor="w")
        self.activity_label.grid(row=0, column=0, sticky="nsew")

        self.activity_input_guide = tk.Frame(self.activity_input_frame)
        self.activity_input_guide.columnconfigure(0, weight=10)
        self.activity_input_guide.rowconfigure(0, weight=10)
        self.activity_input_guide.grid(row=1, column=0, sticky="nsew")
        self.activity_input_guide.grid_propagate(False)

        self.activity_input_text = tk.Entry(self.activity_input_guide, textvariable=tk.StringVar())
        self.activity_input_text.grid(sticky="nsew")

        self.checkbox_input_frame = tk.Frame(self.capability_frame, bg="orange")
        self.checkbox_input_frame.grid(row=2, column=0, sticky="nsew")
        self.checkbox_input_frame.grid_columnconfigure(0, weight=1)
        self.checkbox_input_frame.grid_rowconfigure(0, weight=1)
        self.checkbox_input_frame.grid_rowconfigure(1, weight=1)
        self.checkbox_input_frame.grid_rowconfigure(2, weight=1)
        self.checkbox_input_frame.grid_rowconfigure(3, weight=1)

        self.perm_var = tk.IntVar()
        self.permission_checkbox = tk.Checkbutton(self.checkbox_input_frame, text="Auto Grant Permissions", anchor="w",
                                                  variable=self.perm_var)
        self.permission_checkbox.grid(row=0, column=0, sticky="nsew")
        self.permission_checkbox.select()

        self.noreset_var = tk.IntVar()
        self.noreset_checkbox = tk.Checkbutton(self.checkbox_input_frame, text="No Reset", anchor="w",
                                               variable=self.noreset_var)
        self.noreset_checkbox.grid(row=1, column=0, sticky="nsew")

        self.fullreset_var = tk.IntVar()
        self.fullreset_checkbox = tk.Checkbutton(self.checkbox_input_frame, text="Full Reset", anchor="w",
                                                 variable=self.fullreset_var)
        self.fullreset_checkbox.grid(row=2, column=0, sticky="nsew")
        self.fullreset_checkbox.select()

        self.exitafterparse_var = tk.IntVar()
        self.exitafterparse_checkbox = tk.Checkbutton(self.checkbox_input_frame, text="Exit After Parse", anchor="w",
                                                      variable=self.exitafterparse_var)
        self.exitafterparse_checkbox.grid(row=3, column=0, sticky="nsew")

        self.start_button_frame = tk.Frame(self.capability_frame)
        self.start_button_frame.grid(row=3, column=0, sticky="nsew")
        self.start_button_frame.columnconfigure(0, weight=10)
        self.start_button_frame.rowconfigure(0, weight=10)
        self.start_button_frame.grid_propagate(False)

        self.start_button = tk.Button(self.start_button_frame, text="Start", command=self.start)
        self.start_button.grid(row=0, column=0, sticky="nsew")

        self.output_text_label = tk.Label(self.bottom_portion, text="Output", anchor="nw", justify="left", bg="white",
                                          wraplength=525, width=40)
        self.output_text_label.grid(row=0, column=1, sticky="nsew")

        self.root.mainloop()

    def ddtrace(self, *args):
        selection = get_example_data(self.dropdown_var.get())

        self.app_input_text.delete(0, tk.END)
        self.app_input_text.insert(0, selection["app"])

        self.java_input_text.delete(0, tk.END)
        self.java_input_text.insert(0, selection["java"])

        self.activity_input_text.delete(0, tk.END)
        self.activity_input_text.insert(0, selection["activity"])

    def onclose(self):
        if self.driver is not None:
            self.driver.quit()

        self.root.destroy()

    def out(self, text, reset=False):
        if reset:
            self.output_text = ""
        self.output_text += text + "\n"
        # slice to 2000 chars
        self.output_text = self.output_text[-2000:]
        self.output_text_label.config(text=self.output_text)

    def start(self):
        if self.started:
            self.driver.quit()
            self.started = False
            self.out("ℹ️ Appium server stopped", True)
            self.start_button.config(text="Start")
            self.driver = None
            return

        self.output_text_label.config(text="")
        self.output_text = ""

        app_path = self.app_input_text.get()
        java_path = self.java_input_text.get()
        # srcml_path = self.srcml_input_text.get()
        url = self.url_input_text.get()
        udid = self.udid_input_text.get()
        activity = self.activity_input_text.get()

        if not app_path:
            self.output_text += "Please enter the path to the app apk\n"

        if not java_path:
            self.output_text += "⚠️ Please enter the path to the java file\n"

        # if not srcml_path:
        #    self.output_text += "⚠️ Please enter the path to the libsrcml.dll\n"

        if not url:
            self.output_text += "⚠️ Please enter the Appium server url\n"

        if not udid:
            self.output_text += "⚠️ Please enter the UDID of your Android device\n"

        if not activity:
            self.output_text += "⚠️ Please enter the app start activity\n"

        # Now, let's check if the paths are valid.
        def p(x):
            self.output_text += f"{x}\n"

        check_file_exists(app_path, p)
        check_file_exists(java_path, p)

        # if not os.path.exists(srcml_path):
        #    self.output_text += f"⛔ File: '{srcml_path}' does not exist\n"

        if self.output_text:
            self.output_text_label.config(text=self.output_text)
            return

        self.out("ℹ️ Starting Appium server...", True)

        self.options = UiAutomator2Options()
        self.options.udid = udid
        self.options.app_wait_activity = activity
        self.options.auto_grant_permissions = self.perm_var.get() == 1
        self.options.no_reset = self.noreset_var.get() == 1
        self.options.full_reset = self.fullreset_var.get() == 1
        self.options.app = app_path

        def start_appium_server():
            try:
                # self.driver = webdriver.Remote(url, options=self.options)
                self.driver = new_start_server(self.options)
            except Exception as e:
                print(e)
                self.out(f"⛔ {e}", True)
                self.out("⚠️ Verify URL, app path, package, activity, & review Appium server output.")
                self.output_text_label.config(text=self.output_text)
                self.driver = None
                return

            self.started = True
            self.out("✔️ Appium server started", True)
            self.start_button.config(text="Stop")

            # Get filename from path
            file_name = os.path.basename(java_path)
            # print(file_name)

            start = time.time()
            self.out("ℹ️ Parsing input...", )
            data = None

            try:
                data = parser(file_name, self.java_input_text.get(), self)
            except Exception as e:
                self.out(f"⛔ Unknown parsing error {e}", True)
                self.driver.quit()
                self.started = False
                self.start_button.config(text="Start")
                self.driver = None
                return

            if data is None:
                self.driver.quit()
                self.started = False
                self.start_button.config(text="Start")
                self.driver = None
                return

            output_path = os.path.join(os.path.dirname(__file__), "../../output", f"{file_name}_parsed.json")

            self.out(f"✔️ Parsing complete - output saved to {output_path}")

            if self.exitafterparse_var.get() == 1:
                self.driver.quit()
                self.started = False
                self.start_button.config(text="Start")
                self.driver = None
                return

            self.out(f"⏳ Waiting for the app to load...")
            time.sleep(3)

            self.out("ℹ️ Attempting possible mutable paths...")
            auto_grant_perms = self.perm_var.get() == 1

            try:
                paths = mutator(self.driver, data[0], auto_grant_perms)
            except Exception as e:
                self.out(f"⛔ Unknown mutator error {e}", True)
                self.driver.quit()
                self.started = False
                self.start_button.config(text="Start")
                self.driver = None
                return

            end = time.time()
            paths["time"] = end - start

            output_path = os.path.join(os.path.dirname(__file__), "../../output", f"{file_name}_res.json")
            write_json(paths, output_path)

            self.out(f"✔️ Mutation results saved to {output_path}")

            self.out("ℹ️ Generating task methods...")

            input_path = os.path.join(os.path.dirname(__file__), "../../output")

            try:
                generator(input_path)
            except Exception as e:
                self.out(f"⛔ Unknown generator error {e}", True)
                self.driver.quit()
                self.started = False
                self.start_button.config(text="Start")
                self.driver = None
                return

            self.out(f"✔️ Task methods generated in {input_path}")

            self.driver.quit()
            self.started = False
            self.start_button.config(text="Start")
            self.driver = None

            self.out("ℹ️ Appium server stopped")

        # Start the long-running task in a separate thread
        threading.Thread(target=start_appium_server).start()
