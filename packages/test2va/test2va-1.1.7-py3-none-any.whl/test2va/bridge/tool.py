import os
import shutil
import subprocess
import time

from appium.webdriver.webdriver import WebDriver

from test2va.parser.parser import parser
from test2va.mutator import mutator
from test2va.exceptions import ParseError, MutatorError, GeneratorError
from test2va.generator import generator
from test2va.util import write_json


def parse(app_file_path, java_file_path, driver: WebDriver, events):
    app_file_name = os.path.basename(app_file_path)[:os.path.basename(app_file_path).rfind(".")]

    try:
        date_time = time.strftime("%Y-%m-%d_%H-%M-%S")
        output_path = os.path.join(os.path.dirname(__file__), "../output", f"{app_file_name}_{date_time}")

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        data = parser(os.path.join(output_path, "java_parsed.json"), java_file_path, events)

        return data, output_path
    except Exception as e:
        raise ParseError(f"Error parsing Java file: {java_file_path} - See console for details.", events)


def mutate(driver: WebDriver, data: dict, start: float, output_path: str, events, auto_grant_perms=True):
    try:
        paths = mutator(driver, data[0], auto_grant_perms)
    except Exception as e:
        raise MutatorError("Error mutating app - See console for details.", events)

    end = time.time()
    paths["time"] = end - start

    output_path = os.path.join(output_path, f"mutate_res.json")
    write_json(paths, output_path)

    return output_path


def generate(driver: WebDriver, output_path, events):
    input_path = output_path

    try:
        generator(input_path)
    except Exception as e:
        raise GeneratorError("Error generating task methods - See console for details.", events)

    return input_path


def get_cap_type(caps, cap):
    for c in caps:
        if c[0] == cap:
            return c[1]


def format_caps(cap_cache: dict[str, str], cap_data) -> dict[str, str | int | bool]:
    caps = {}

    for cap, val in cap_cache.items():
        cap_type = get_cap_type(cap_data, cap)
        if isinstance(cap_type, str):
            caps[cap] = val
        elif cap_type == "bool":
            caps[cap] = val.lower() == "true"
        elif cap_type == "int":
            caps[cap] = int(val)
        else:
            caps[cap] = val

    return caps


def check_node_installed():
    try:
        subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


def check_npm_installed():
    npm_path = shutil.which("npm")
    if npm_path is None:
        print("npm is not installed or not found in the system PATH.")
        return
    print(f"npm found at: {npm_path}")
    return npm_path


def check_npm_appium_install():
    npm_path = check_npm_installed()

    if npm_path is None:
        return False

    try:
        # Ensure the environment PATH is included
        env = os.environ.copy()
        result = subprocess.run([npm_path, "list", "-g", "appium"], capture_output=True, text=True, env=env)
        print(f"npm list output: {result.stdout}")
        print(f"npm list errors: {result.stderr}")
        if "appium" in result.stdout:
            print("Appium is installed globally.")
            return True
        else:
            print("Appium is not installed globally.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"npm list command failed with error: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Command stderr: {e.stderr}")
        return False


def install_appium():
    npm_path = check_npm_installed()
    if npm_path is None:
        return

    try:
        env = os.environ.copy()
        result = subprocess.run([npm_path, "install", "-g", "appium"], check=True, text=True, capture_output=True,
                                env=env)
        print(f"npm install output: {result.stdout}")
        print(f"npm install errors: {result.stderr}")
        print("Appium installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"npm install command failed with error: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Command stderr: {e.stderr}")
        return False


def check_uia2_driver_install():
    appium_path = shutil.which("appium")

    if appium_path is None:
        print("appium command not found in PATH.")
        return

    try:
        env = os.environ.copy()
        result = subprocess.run([appium_path, "driver", "list", "--installed"], capture_output=True, text=True, check=True,
                                env=env)
        # for some reason the output is in stderr
        if "uiautomator2" in result.stdout or "uiautomator2" in result.stderr:
            print("UiAutomator2 driver is installed.")
            return True
        else:
            print("UiAutomator2 driver is not installed.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"appium driver list command failed with error: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Command stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print("appium command not found in PATH.")
        return False


def install_uia2_driver():
    appium_path = shutil.which("appium")

    if appium_path is None:
        print("appium command not found in PATH.")
        return

    try:
        env = os.environ.copy()
        result = subprocess.run([appium_path, "driver", "install", "uiautomator2"], capture_output=True, text=True,
                                check=True,
                                env=env)
        print(f"appium driver install output: {result.stdout}")
        print(f"appium driver install errors: {result.stderr}")
        print("UiAutomator2 driver installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"appium driver install command failed with error: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Command stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print("appium command not found in PATH.")
        return False
