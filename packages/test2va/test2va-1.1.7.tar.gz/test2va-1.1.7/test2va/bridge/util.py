import os


def check_file_exists(file_path, print_func=print):
    exists = os.path.exists(file_path)

    if not exists:
        print_func(f"⛔ File: '{file_path}' does not exist\n")
        return False

    return True
