import subprocess
import time

from appium.options.android import UiAutomator2Options
from appium import webdriver
from appium.webdriver.appium_service import AppiumService

from test2va.exceptions import AppiumServerError


def get_capability_options():
    return [
        ("adb_exec_timeout", "int",
         "Maximum number of milliseconds to wait until single ADB command is executed. 20000 ms by default."),
        ("adb_port", "int", "Number of the port on the host machine where ADB is running. 5037 by default."),
        ("allow_delay_adb", "bool",
         "Being set to false prevents emulator to use -delay-adb feature to detect its startup."),
        ("allow_test_packages", "bool",
         "If set to true then it would be possible to use packages built with the test flag for the automated testing (literally adds -t flag to the adb install command). false by default."),
        ("android_install_timeout", "int",
         "Maximum amount of milliseconds to wait until the application under test is installed. 90000 ms by default."),
        # ("app", "str",
        # "Full path to the application to be tested (the app must be located on the same machine where the server is running). Both .apk and .apks application extensions are supported. Could also be an URL to a remote location. If neither of the app, apppackage or browsername capabilities are provided then the driver starts from the Dashboard and expects the test knows what to do next. Do not provide both app and browsername capabilities at once."),
        ("app_activity", "str",
         "Main application activity identifier. If not provided then UiAutomator2 will try to detect it automatically from the package provided by the app capability."),
        ("app_package", "str",
         "Application package identifier to be started. If not provided then UiAutomator2 will try to detect it automatically from the package provided by the app capability."),
        ("app_wait_activity", "str",
         "Identifier of the first activity that the application invokes. If not provided then equals to appactivity."),
        ("app_wait_duration", "int",
         "Maximum amount of milliseconds to wait until the application under test is started (e. g. an activity returns the control to the caller). 20000 ms by default."),
        ("app_wait_for_launch", "bool",
         "Whether to block until the app under test returns the control to the caller after its activity has been started by Activity Manager (true, the default value) or to continue the test without waiting for that (false)."),
        ("app_wait_package", "str",
         "Identifier of the first package that is invoked first. If not provided then equals to apppackage."),
        ("auto_grant_permissions", "bool",
         "Whether to grant all the requested application permissions automatically when a test starts(true). The targetSdkVersion in the application manifest must be greater or equal to 23 and the Android version on the device under test must be greater or equal to Android 6 (API level 23) to grant permissions. Applications whose targetSdkVersion is lower than or equal to 22 must be reinstalled to grant permissions, for example, by setting the fullreset capability as true for Android 6+ devices. If your app needs some special security permissions, like access to notifications or media recording, consider using mobile: changePermissions extension with appops target. false by default."),
        ("auto_launch", "bool",
         "Whether to launch the application under test automatically (true, the default value) after a test starts."),
        ("auto_webview", "bool",
         "If set to true then UiAutomator2 driver will try to switch to the web view with name WEBVIEW_ + apppackage after the session is started. For example, if apppackage capability is set to com.mypackage then WEBVIEW_com.mypackage will be used. false by default."),
        ("auto_webview_name", "str",
         "Set the name of webview context in which UiAutomator2 driver will try to switch if autowebview capability is set to true (available since driver version 2.9.1). Has priority over using the apppackage value in webview name. For example, if autowebviewname capability is set to myWebviewName then WEBVIEW_myWebviewName will be used. Unset by default."),
        ("auto_webview_timeout", "int",
         "Set the maximum number of milliseconds to wait until a web view is available if autowebview capability is set to true. 2000 ms by default."),
        # ("automation_name", "str",
        # "Must always be set to uiautomator2. Values of automationname are compared case-insensitively."),
        ("avd", "str",
         "The name of Android emulator to run the test on. The names of currently installed emulators could be listed using avdmanager list avd command. If the emulator with the given name is not running then it is going to be launched on automated session startup."),
        ("avd_args", "str",
         "Either a string or an array of emulator command line arguments. If arguments contain the -wipe-data one then the emulator is going to be killed on automated session startup in order to wipe its data."),
        ("avd_env", "str", "Mapping of emulator environment variables."),
        ("avd_launch_timeout", "int",
         "Maximum number of milliseconds to wait until Android Emulator is started. 60000 ms by default."),
        ("avd_ready_timeout", "int",
         "Maximum number of milliseconds to wait until Android Emulator is fully booted and is ready for usage. 60000 ms by default."),
        ("build_tools_version", "str",
         "The version of Android build tools to use. By default UiAutomator2 driver uses the most recent version of build tools installed on the machine, but sometimes it might be necessary to give it a hint (let say if there is a known bug in the most recent tools version). Example: 28.0.3."),
        ("chrome_logging_prefs", "str",
         "Chrome logging preferences mapping. Basically the same as goog:loggingPrefs. It is set to {browser: ALL} by default."),
        ("chrome_options", "str", "A mapping, that allows to customize chromedriver options."),
        ("chromedriver_args", "str", "Array of chromedriver command line arguments."),
        ("chromedriver_chrome_mapping_file", "str",
         "Full path to the chromedrivers mapping file. This file is used to statically map webview/browser versions to the chromedriver versions that are capable of automating them."),
        ("chromedriver_disable_build_check", "bool",
         "Being set to true disables the compatibility validation between the current chromedriver and the destination browser/web view."),
        ("chromedriver_executable", "str", "Full path to the chromedriver executable on the server file system."),
        ("chromedriver_executable_dir", "str",
         "Full path to the folder where chromedriver executables are located. This folder is used then to store the downloaded chromedriver executables if automatic download is enabled."),
        ("chromedriver_port", "int",
         "The port number to use for Chromedriver communication. Any free port number is selected by default if unset."),
        ("chromedriver_ports", "str",
         "Array of possible port numbers to assign for Chromedriver communication. If none of the port in this array is free then an error is thrown."),
        ("chromedriver_use_system_executable", "bool",
         "Set it to true in order to enforce the usage of chromedriver, which gets downloaded by Appium automatically upon installation. This driver might not be compatible with the destination browser or a web view. false by default."),
        ("clear_device_logs_on_start", "bool",
         "If set to true then UiAutomator2 deletes all the existing logs in the device buffer before starting a new test."),
        ("device_name", "str",
         "The name of the device under test (actually, it is not used to select a device under test). Consider setting udid for real devices and avd for emulators instead."),
        ("disable_suppress_accessibility_service", "bool",
         "Being set to true tells the instrumentation process to not suppress accessibility services during the automated test. This might be useful if your automated test needs these services. false by default."),
        ("disable_window_animation", "bool",
         "Whether to disable window animations when starting the instrumentation process. The animation scale will be restored automatically after the instrumentation process ends for API level 26 and higher. The animation scale could remain if the session ends unexpectedly for API level 25 and lower. false by default."),
        ("dont_stop_app_on_reset", "bool",
         "Set it to true if you don't want the application to be restarted if it was already running. If noreset is falsy, then the app under test is going to be restarted if either this capability is falsy (the default behavior) or forceapplaunch is set to true. false by default."),
        ("enable_webview_details_collection", "bool",
         "Whether to retrieve extended web views information using devtools protocol. Enabling this capability helps to detect the necessary chromedriver version more precisely. true by default since Appium 1.22.0, false if lower than 1.22.0."),
        ("enforce_app_install", "bool",
         "If set to true then the application under test is always reinstalled even if a newer version of it already exists on the device under test. This capability has no effect if noreset is set to true. false by default."),
        ("ensure_webviews_have_pages", "bool",
         "Whether to skip web views that have no pages from being shown in getContexts output. The driver uses devtools connection to retrieve the information about existing pages. true by default since Appium 1.19.0, false if lower than 1.19.0."),
        ("extract_chrome_android_package_from_context_name", "bool",
         "If set to true, tell chromedriver to attach to the android package we have associated with the context name, rather than the package of the application under test. false by default."),
        ("force_app_launch", "bool",
         "Set it to true if you want the application under test to be always forcefully restarted on session startup even if noreset is true, and the app was already running. If noreset is falsy, then the app under test is going to be restarted if either this capability set to true or dontstopapponreset is falsy (the default behavior). false by default. Available since driver version 2.12."),
        ("full_reset", "bool",
         "Being set to true always enforces the application under test to be fully uninstalled before starting a new session. false by default."),
        ("gps_enabled", "bool",
         "Sets whether to enable (true) or disable (false) GPS service in the Emulator. Unset by default, which means to not change the current value."),
        ("hide_keyboard", "bool",
         "Being set to true hides the on-screen keyboard while the session is running. Use it instead of the legacy unicodekeyboard one (which will be dropped in the future). This effect is achieved by assigning a custom artificial input method. Only use this feature for special/exploratory cases as it violates the way your application under test is normally interacted with by a human. Setting this capability explicitly to false enforces adb shell ime reset call on session startup, which resets the currently selected/enabled IMEs to the default ones as if the device is initially booted with the current locale. undefined by default."),
        ("ignore_hidden_api_policy_error", "bool",
         "Being set to true ignores a failure while changing hidden API access policies to enable access to non-SDK interfaces. Could be useful on some devices, where access to these policies has been locked by its vendor. false by default."),
        ("injected_image_properties", "str",
         "Allows adjusting of injected image properties, like size, position or rotation. The image itself is expected to be injected by mobile: injectEmulatorCameraImage extension. It is also mandatory to provide this capability if you are going to use the injection feature on a newly created/resetted emulator as it enforces emulator restart, so it could properly reload the modified image properties. The value itself is a map, where possible keys are size, position and rotation. All of them are optional. If any of values is not provided then the following defaults are used: {size: {scaleX: 1, scaleY: 1}, position: {x: 0, y: 0, z: -1.5}, rotation: {x: 0, y: 0, z: 0}}. The size value contains scale multipliers for X and Y axes. The position contains normalized coefficients for X/Y/Z axes, where 0 means it should be centered in the viewport. Values in the rotation are measured in degrees respectively for X, Y and Z axis. The capability is available since the driver version 3.6.0."),
        ("intent_action", "str",
         "Set an optional intent action to be applied when starting the given appactivity by Activity Manager. Defaults to android.intent.action.MAIN."),
        ("intent_category", "str",
         "Set an optional intent category to be applied when starting the given appactivity by Activity Manager. Defaults to android.intent.category.LAUNCHER."),
        ("intent_flags", "str",
         "Set an optional intent flags to be applied when starting the given appactivity by Activity Manager. Defaults to 0x10200000 (FLAG_ACTIVITY_NEW_TASK | FLAG_ACTIVITY_RESET_TASK_IF_NEEDED flags)."),
        ("is_headless", "bool",
         "If set to true then emulator starts in headless mode (e.g. no UI is shown). It is only applied if the emulator is not running before the test starts. false by default."),
        ("key_alias", "str",
         "The alias of the key in the keystore file provided in keystorepath capability. This capability is used in combination with usekeystore, keystorepath, keystorepassword, keyalias and keypassword capabilities. Unset by default."),
        ("key_password", "str",
         "The password of the key in the keystore file provided in keystorepath capability. This capability is used in combination with usekeystore, keystorepath, keystorepassword, keyalias and keypassword capabilities. Unset by default."),
        ("keystore_password", "str",
         "The password to the keystore file provided in keystorepath capability. This capability is used in combination with usekeystore, keystorepath, keystorepassword, keyalias and keypassword capabilities. Unset by default."),
        ("keystore_path", "str",
         "The full path to the keystore file on the server filesystem. This capability is used in combination with usekeystore, keystorepath, keystorepassword, keyalias and keypassword capabilities. Unset by default."),
        ("language", "str",
         "Name of the language to extract application strings for. Strings are extracted for the current system language by default. Also sets the language for the app under test. If language is provid"),
        ("locale", "str",
         "Sets the locale for the app under test. If locale is provided then language is also required to be set. The combination of both capability values must be a known locale and should be present in the list of available locales returned by the ICU's getAvailableULocales() method. The full list of supported locales is also dumped into the logcat output on failure. Example: US, JP"),
        ("locale_script", "str",
         "Canonical name of the locale to be set for the app under test, for example Hans in zh-Hans-CN."),
        ("logcat_filter_specs", "str",
         "Series of tag[:priority] where tag is a log component tag (or * for all) and priority is: V Verbose, D Debug, I Info, W Warn, E Error, F Fatal, S Silent (supress all output). * means *:d and tag by itself means tag:v. If not specified on the commandline, filterspec is set from ANDROID_LOG_TAGS. If no filterspec is found, filter defaults to *:I."),
        ("logcat_format", "str",
         "The log print format, where format is one of: brief process tag thread raw time threadtime long. threadtime is the default value."),
        ("mjpeg_screenshot_url", "str",
         "The URL of a service that provides realtime device screenshots in MJPEG format. If provided then the actual command to retrieve a screenshot will be requesting pictures from this service rather than directly from the server"),
        ("mjpeg_server_port", "int",
         "The number of the port on the host machine that UiAutomator2 server starts the MJPEG server on. If not provided then the screenshots broadcasting service on the remote device does not get expos"),
        ("mock_location_app", "str",
         "Sets the package identifier of the app, which is used as a system mock location provider since Appium 1.18.0+. This capability has no effect on emulators. If the value is set to null or an empty string, then Appium will skip the mocked location provider setup procedure. Defaults to Appium Setting package identifier (io.appium.settings). Termination of a mock location provider application resets the mocked location data."),
        ("native_web_screenshot", "bool",
         "Whether to use screenshoting endpoint provided by UiAutomator framework (true) rather than the one provided by chromedriver (false, the default value). Use it when you experience issues with the latter."),
        ("network_speed", "str",
         "Sets the desired network speed limit for the emulator. It is only applied if the emulator is not running before the test starts."),
        ("new_command_timeout", "int",
         "How long (in seconds) the driver should wait for a new command from the client before assuming the client has stopped sending requests. After the timeout the session is going to be deleted. 60 seconds by default. Setting it to zero disables the timer."),
        ("no_reset", "bool",
         "Prevents the device to be reset before the session startup if set to true. This means that the application under test is not going to be terminated neither its data cleaned. false by default."),
        ("no_sign", "bool",
         "Set it to true in order to skip application signing. By default all apps are always signed with the default Appium debug signature if they don't have any. This capability cancels all the signing checks and makes the driver to use the application package as is. This capability does not affect .apks packages as these are expected to be already signed."),
        ("optional_intent_arguments", "str",
         "Set an optional intent arguments to be applied when starting the given appactivity by Activity Manager."),
        ("other_apps", "str",
         "Allows to set one or more comma-separated paths to Android packages that are going to be installed along with the main application under test. This might be useful if the tested app has dependencies."),
        ("platform_version", "str",
         "The platform version of an emulator or a real device. This capability is used for device autodetection if udid is not provided."),
        ("print_page_source_on_find_failure", "bool",
         "Enforces the server to dump the actual XML page source into the log if any error happens. false by default."),
        ("recreate_chrome_driver_sessions", "bool",
         "If this capability is set to true then chromedriver session is always going to be killed and then recreated instead of just suspending it on context switching. false by default."),
        ("remote_adb_host", "str",
         "Address of the host where ADB is running (the value of -H ADB command line option). Unset by default."),
        ("remote_apps_cache_limit", "int",
         "Sets the maximum amount of application packages to be cached on the device under test. This is needed for devices that don't support streamed installs (Android 7 and below), because ADB must push app packages to the device first in order to install them, which takes some time. Setting this capability to zero disables apps caching. 10 by default."),
        ("should_terminate_app", "bool",
         "Set it to true if you want the application under test to be always terminated on session end even if noreset is true. If noreset is falsy, then the app under test is going to be terminated if dontstopapponreset is also falsy (the default behavior). false by default."),
        ("show_chromedriver_log", "bool",
         "If set to true then all the output from chromedriver binary will be forwarded to the Appium server log. false by default."),
        ("skip_device_initialization", "bool",
         "If set to true then device startup checks (whether it is ready and whether Settings app is installed) will be canceled on session creation. Could speed up the session creation if you know what you are doing. false by default."),
        ("skip_logcat_capture", "bool",
         "Skips to start capturing logs such as logcat. It might improve network performance. Log-related commands won't work if the capability is enabled. Defaults to false."),
        ("skip_server_installation", "bool",
         "Skip the UiAutomator2 Server component installation on the device under test and all the related checks if set to true. This could help to speed up the session startup if you know for sure the correct server version is installed on the device. In case the server is not installed or an incorrect version of it is installed then you may get an unexpected error later. false by default."),
        ("skip_unlock", "bool",
         "Whether to skip the check for lock screen presence (true). The default driver behavior is to verify the presence of the screen lock (e.g. false value of the capability) before starting the test and to unlock that (which sometimes might be unstable). Note, that this operation takes some time, so it is highly recommended to set this capability to true and disable screen locking on device(s) under test."),
        ("suppress_kill_server", "bool",
         "Being set to true prevents the driver from ever killing the ADB server explicitly. Could be useful if ADB is connected wirelessly. false by default."),
        ("system_port", "int",
         "The number of the port on the host machine used for the UiAutomator2 server. By default the first free port from 8200..8299 range is selected. It is recommended to set this value if you are running parallel tests on the same machine."),
        ("time_zone", "str",
         "Overrides the current device's time zone since the driver version 3.1.0. This change is preserved until the next override. The time zone identifier must be a valid name from the list of available time zone identifiers, for example Europe/Kyiv."),
        ("udid", "str",
         "UDID of the device to be tested. Could be retrieved from adb devices -l output. If unset then the driver will try to use the first connected device. Always set this capability if you run parallel tests."),
        ("uiautomator2_server_install_timeout", "int",
         "The maximum number of milliseconds to wait until UiAutomator2Server is installed on the device. 20000 ms by default."),
        ("uiautomator2_server_launch_timeout", "int",
         "The maximum number of milliseconds to wait until UiAutomator2Server is listening on the device. 30000 ms by default."),
        ("uiautomator2_server_read_timeout", "int",
         "The maximum number of milliseconds to wait for a HTTP response from UiAutomator2Server. Only values greater than zero are accepted. If the given value is too low then expect driver commands to fail with timeout of Xms exceeded error. 240000 ms by default."),
        ("uninstall_other_packages", "str",
         "Allows to set one or more comma-separated package identifiers to be uninstalled from the device before a test starts."),
        ("unlock_key", "str", "Allows to set an unlock key."),
        ("unlock_strategy", "str", "Either locksettings (default) or uiautomator."),
        ("unlock_success_timeout", "int",
         "Maximum number of milliseconds to wait until the device is unlocked. 2000 ms by default."),
        ("unlock_type", "str", "Set one of the possible types of Android lock screens to unlock."),
        ("use_keystore", "bool",
         "Whether to use a custom keystore to sign the app under test. false by default, which means apps are always signed with the default Appium debug certificate (unless canceled by nosign capability). This capability is used in combination with keystorepath, keystorepassword, keyalias and keypassword capabilities."),
        ("user_profile", "int",
         "Integer identifier of a user profile. By default the app under test is installed for the currently active user, but in case it is necessary to test how the app performs while being installed for a user profile, which is different from the current one, then this capability might come in handy."),
        ("webview_devtools_port", "int",
         "The local port number to use for devtools communication. By default the first free port from 10900..11000 range is selected. Consider setting the custom value if you are running parallel tests."),
    ]


def check_capability_type(cap: str, value: str):
    cap = find_capability(cap)
    if cap is None:
        return False

    t = cap[1]

    if t == "str":
        return True
    elif t == "int":
        try:
            int(value)
            return True
        except ValueError:
            return False
    elif t == "bool":
        return value.lower() == "true" or value.lower() == "false"

    return False


def find_capability(cap: str):
    caps = get_capability_options()
    for c in caps:
        if c[0] == cap:
            return c
    return None


def find_running_device():
    command = ["adb", "devices"]
    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout

    lines = output.split("\n")
    if len(lines) < 2:
        return None

    devices = []
    for line in lines[1:]:
        if not line:
            continue

        device = line.split("\t")[0]
        devices.append(device)

    return devices


def start_server(url: str, opts: UiAutomator2Options):
    print("ℹ️ Starting Appium server...")

    try:
        driver = webdriver.Remote(url, options=opts)
        print("✔️ Appium server started")
        return driver
    except Exception as e:
        print(e)
        print("⚠️ Verify URL, app path, package, activity, & review Appium server output.")
        exit(1)


def new_start_server(opts: UiAutomator2Options, events):
    try:
        apps = AppiumService()
        apps.start(args=[
            '--address', 'localhost',
            '-p', '4723',
            '--base-path', '/wd/hub',
            '--relaxed-security',
        ])
        driver = webdriver.Remote("http://localhost:4723/wd/hub", options=opts)
        return driver, apps
    except Exception as e:
        raise AppiumServerError("Appium server failed to start. Verify APK path, capabilities, device udid, & review "
                                "error output in console. Also verify appium npm installation.", events)


def wait_app_load():
    time.sleep(3)
