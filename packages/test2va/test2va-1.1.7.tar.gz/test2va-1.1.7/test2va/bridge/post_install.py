import os

ex_asset_path = os.path.join(os.path.dirname(__file__), "../examples", "NOTES")
apk_path = os.path.abspath(os.path.join(ex_asset_path, "another-notes-app.apk"))
cl_path = os.path.abspath(os.path.join(ex_asset_path, "NOTES_CreateLabel.java"))
sls_path = os.path.abspath(os.path.join(ex_asset_path, "NOTES_SetLeftSwipeToDelete.java"))

profile_path = os.path.join(os.path.dirname(__file__), "../profiles")

create_label = '{"apk": ' + f'"{apk_path}"' + ', "caps": {"app_wait_activity": ' \
                                              '"com.maltaisn.notes.ui.main.MainActivity", "auto_grant_permissions": ' \
               + 'true, "full_reset": true, "no_reset": false}, "java_path": ' + f'"{cl_path}"' + ', "udid": ' \
                                                                                                  '"emulator-5554"}'

set_left_swipe = '{"apk": ' + f'"{apk_path}"' + ', "caps": {"app_wait_activity": ' \
                                                '"com.maltaisn.notes.ui.main.MainActivity", "auto_grant_permissions": ' \
                 + 'true, "full_reset": true, "no_reset": false}, "java_path": ' + f'"{sls_path}"' + ', "udid": ' \
                                                                                                     '"emulator-5554"}'
create_label = create_label.replace("\\", "\\\\")
set_left_swipe = set_left_swipe.replace("\\", "\\\\")

create_label_name = "EX_NOTES_CreateLabel"
set_left_swipe_name = "EX_NOTES_SetLeftSwipeToDe"


def create_examples():
    if os.path.exists(os.path.join(profile_path, create_label_name)) and os.path.exists(
            os.path.join(profile_path, set_left_swipe_name)):
        return

    # First create a folder for each profile name in the profiles directory
    os.makedirs(os.path.join(profile_path, create_label_name), exist_ok=True)
    os.makedirs(os.path.join(profile_path, set_left_swipe_name), exist_ok=True)

    # Then in each folder, create a file "profile.json" that has the content of each profile
    with open(os.path.join(profile_path, create_label_name, "profile.json"), "w") as f:
        f.write(create_label)

    with open(os.path.join(profile_path, set_left_swipe_name, "profile.json"), "w") as f:
        f.write(set_left_swipe)


if __name__ == "__main__":
    create_examples()
