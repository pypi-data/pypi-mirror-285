import os
import time

from appium.options.android import UiAutomator2Options

from test2va.bridge import format_caps, check_node_installed, check_npm_appium_install, install_appium, \
    check_uia2_driver_install, install_uia2_driver, new_start_server, parse, wait_app_load, mutate, generate
from test2va.exceptions import NoJavaData, CapTypeMismatch, NodeNotInstalled, ExecutionStopped, \
    AppiumInstallationError


class Event:
    def __init__(self):
        self.handlers = []

    def connect(self, func):
        self.handlers.append(func)

    def fire(self, *args, **kwargs):
        for handler in self.handlers:
            handler(*args, **kwargs)


class ExecEvents:
    def __init__(self):
        self.on_start = Event()
        self.on_finish = Event()
        self.on_error = Event()
        self.on_progress = Event()
        self.on_log = Event()
        self.on_success = Event()


class ToolExec:
    def __init__(self, udid: str, apk: str, added_caps: dict[str, str], cap_data, j_path: str = None, j_code: str = None):
        self.events = ExecEvents()
        self._connect_default()

        self.apk = apk
        self.udid = udid
        self.j_code = j_code
        self.j_path = j_path
        self.caps = added_caps
        self.cap_data = cap_data
        self.temp_java = None
        self.options = UiAutomator2Options()
        self.driver = None
        self.app_service = None
        self.start = None

        self.stopped = False

    def execute(self):
        self.events.on_start.fire()

        if self.j_code is None and self.j_path is None:
            raise NoJavaData("No Java source code or path provided. See console for details.", self.events)

        if self.j_code is not None:
            self.temp_java = os.path.join(os.path.dirname(__file__), "../output/temp_java.java")
            with open(self.temp_java, "w") as f:
                f.write(self.j_code)

            self.j_path = self.temp_java

        self.caps = format_caps(self.caps, self.cap_data)
        self.options.udid = self.udid
        self.options.app = self.apk
        self.options.automation_name = "UiAutomator2"

        for cap, val in self.caps.items():
            try:
                setattr(self.options, cap, val)
            except Exception:
                raise CapTypeMismatch(f"Capability type mismatch for {cap}. See console for details.", self.events)

        self.events.on_progress.fire("Checking Node installation")

        if not check_node_installed():
            raise NodeNotInstalled("Node installation not found. Install it here: "
                                   "https://nodejs.org/en/download/package-manager. Make sure it is added to PATH.",
                                   self.events)

        self.events.on_success.fire("Node installation found")
        self.events.on_progress.fire("Checking Appium installation")

        if not check_npm_appium_install():
            self.events.on_progress.fire("Appium installation not found. Attempting installation")
            install_success = install_appium()

            if not install_success:
                raise AppiumInstallationError("Appium installation failed. Use 'npm install -g appium' to install "
                                              "manually. See console for details.", self.events)

            self.events.on_success.fire("Appium installation successful")
        else:
            self.events.on_success.fire("Appium installation found")

        self.events.on_progress.fire("Checking UiAutomator2 driver installation")

        if not check_uia2_driver_install():
            self.events.on_progress.fire("UiAutomator2 driver installation not found. Attempting installation")

            install_success = install_uia2_driver()

            if not install_success:
                raise AppiumInstallationError("UiAutomator2 driver installation failed. Use 'appium driver install "
                                              "uiautomator2' to install manually. See console for details.", self.events)

            self.events.on_success.fire("UiAutomator2 driver installation successful")
        else:
            self.events.on_success.fire("UiAutomator2 driver installation found")

        self.events.on_progress.fire("Starting Appium server")

        self.driver, self.app_service = new_start_server(self.options, self.events)

        self.events.on_success.fire("Appium server started")

        self.start = time.time()

        self.events.on_progress.fire("Parsing java source code")

        data, output_path = parse(self.apk, self.j_path, self.driver, self.events)

        self.events.on_success.fire(f"Parsing complete - output saved to {os.path.abspath(output_path)}")

        self.events.on_progress.fire("Waiting for app to load")
        wait_app_load()

        self.events.on_progress.fire("Attempting possible mutable paths")
        m_out_path = mutate(self.driver, data, self.start, output_path, self.events)

        self.events.on_success.fire(f"Mutation complete - output saved to {os.path.abspath(m_out_path)}")

        self.events.on_progress.fire("Generating results and task methods")

        method_path = generate(self.driver, output_path, self.events)

        self.events.on_success.fire(f"Generation complete - output saved to {os.path.abspath(method_path)}")

        self.driver.quit()

        self.events.on_log.fire("Appium server stopped")

        self.events.on_finish.fire()

    def stop(self):
        self.events.on_log.fire("Stop request received. Stopping execution when possible...")
        self.stopped = True

    def _connect_default(self):
        # Remove temp java
        self.events.on_error.connect(self._remove_temp_java)
        self.events.on_finish.connect(self._remove_temp_java)
        self.events.on_finish.connect(self._on_stop)
        self.events.on_progress.connect(self._on_prog_stop_check)

    def _remove_temp_java(self, _=None, __=None):
        if self.temp_java is not None and os.path.exists(self.temp_java):
            os.remove(self.temp_java)

    def _on_prog_stop_check(self, _):
        if self.stopped:
            raise ExecutionStopped("Execution stopped by user", self.events)

    def _on_stop(self):
        if self.app_service is not None:
            try:
                self.app_service.stop()
            except Exception:
                pass

        if self.driver is not None:
            try:
                self.driver.quit()
            except Exception:
                pass

        self.app_service = None
        self.driver = None
