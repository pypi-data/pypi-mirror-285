import json
import os

prof_path = os.path.join(os.path.dirname(__file__), "../profiles")
max_prof_name_len = 28


def save_profile(name, apk="", caps={}, udid="", j_path="", j_code=None):
    name = name[:max_prof_name_len]

    if not os.path.exists(os.path.join(prof_path, name)):
        os.makedirs(os.path.join(prof_path, name))

    prof_dir = os.path.join(prof_path, name)

    if j_code is not None:
        with open(os.path.join(prof_dir, "java_src_code.java"), "w") as file:
            file.write(j_code)
        j_path = os.path.join(prof_dir, "java_src_code.java")

    if len(apk) > 0:
        apk = os.path.abspath(apk)

    if len(j_path) > 0:
        j_path = os.path.abspath(j_path)

    data = {
        "apk": apk,
        "caps": caps,
        "java_path": j_path,
        "udid": udid
    }

    with open(os.path.join(prof_dir, "profile.json"), "w") as file:
        json.dump(data, file)

    return prof_dir


def delete_profile(name):
    prof_dir = os.path.join(prof_path, name)
    if os.path.exists(prof_dir):
        for root, dirs, files in os.walk(prof_dir):
            for file in files:
                os.remove(os.path.join(root, file))
        os.rmdir(prof_dir)
        return True
    return False


def find_profile(name):
    profs = get_profiles()
    for prof in profs:
        if prof["name"] == name:
            return prof
    return None


def get_profiles():
    profiles = []
    for root, dirs, files in os.walk(prof_path):
        for name in dirs:
            prof = os.path.join(prof_path, name, "profile.json")
            if not os.path.exists(prof):
                continue

            with open(prof, "r") as file:
                data = json.load(file)

            profiles.append({
                "name": name,
                "apk": data["apk"],
                "caps": data["caps"],
                "java_path": data["java_path"],
                "udid": data["udid"]
            })

    return profiles
