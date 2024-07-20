import os
import importlib.util


def find_module_path(module_name):
    spec = importlib.util.find_spec(module_name)
    if spec is not None:
        return spec.origin
    else:
        return None


def replace_line_in_file(file_path, start_string, new_line):
    # Read the original content of the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Replace the line that starts with the specified string
    for i, line in enumerate(lines):
        if line.strip().startswith(start_string):
            lines[i] = new_line.replace("\\", "\\\\") + '\n'
            break

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.writelines(lines)


def modify_srcml(libsrcml_path: str):
    if not os.path.exists(libsrcml_path):
        raise FileNotFoundError(f"File {libsrcml_path} not found.")

    srcml_globals_path = find_module_path('pylibsrcml.globals')
    if srcml_globals_path is None:
        raise FileNotFoundError("Could not find pylibsrcml.globals. Is pylibsrcml installed?")

    replace_line_in_file(srcml_globals_path, 'libsrcml = cdll.LoadLibrary(', f'libsrcml = cdll.LoadLibrary("{libsrcml_path}")')