import os

from test2va.bridge import save_profile, get_profiles, delete_profile, find_profile, check_file_exists

prof_path = os.path.join(os.path.dirname(__file__), "../profiles")


def check_prof_path():
    if not os.path.exists(prof_path):
        os.makedirs(prof_path)


def profile_apk(name, path):
    check_prof_path()
    prof = find_profile(name)

    if prof is None:
        print(f"Profile '{name}' not found. Create the profile using 'test2va profile create {name}'.")
        return

    exists = check_file_exists(path, lambda _: None)
    if not exists:
        print(f"APK path '{path}' not found.")
        return

    if not path.endswith(".apk"):
        print(f"APK path '{path}' is not an APK file.")
        return

    save_profile(name, path, prof["caps"], prof["udid"], prof["java_path"])
    print(f"APK path added to profile '{name}'.")


def profile_create(name):
    check_prof_path()
    save_profile(name)
    print(f"Profile '{name}' created successfully. Use 'test2va profile view {name}' to view the profile details.")


def profile_delete(name):
    check_prof_path()
    found = delete_profile(name)
    if not found:
        print(f"Profile '{name}' not found.")
        return
    print(f"Profile '{name}' deleted successfully.")


def profile_java(name, path):
    check_prof_path()
    prof = find_profile(name)

    if prof is None:
        print(f"Profile '{name}' not found. Create the profile using 'test2va profile create {name}'.")
        return

    exists = check_file_exists(path, lambda _: None)
    if not exists:
        print(f"Java source code path '{path}' not found.")
        return

    if not path.endswith(".java"):
        print(f"Java source code path '{path}' is not a Java file.")
        return

    save_profile(name, prof["apk"], prof["caps"], prof["udid"], path)

    print(f"Java source code path added to profile '{name}'.")


def profile_list():
    check_prof_path()
    profs = get_profiles()
    if len(profs) == 0:
        print("No profiles found.")
        return

    print("Profiles:")
    for prof in profs:
        name = prof["name"]
        print(f"  {name}")


def profile_udid(name, udid):
    check_prof_path()
    prof = find_profile(name)

    if prof is None:
        print(f"Profile '{name}' not found. Create the profile using 'test2va profile create {name}'.")
        return

    save_profile(name, prof["apk"], prof["caps"], udid, prof["java_path"])
    print(f"UDID added to profile '{name}'.")


def profile_view(name):
    check_prof_path()
    prof = find_profile(name)

    if prof is None:
        print(f"Profile '{name}' not found.")
        return

    print(f"Profile '{name}':")
    print(f"  APK: {prof['apk']}")
    print(f"  Java: {prof['java_path']}")
    print(f"  UDID: {prof['udid']}")
    print("  Capabilities:")
    for cap, value in prof["caps"].items():
        print(f"    {cap}: {value}")
