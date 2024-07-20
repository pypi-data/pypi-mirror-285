common_permissions = [
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.CAMERA",
    "android.permission.READ_CONTACTS",
    "android.permission.WRITE_CONTACTS",
    "android.permission.GET_ACCOUNTS",
    "android.permission.ACCESS_WIFI_STATE",
    "android.permission.CHANGE_WIFI_STATE",
    "android.permission.BLUETOOTH",
    "android.permission.BLUETOOTH_ADMIN",
    "android.permission.READ_PHONE_STATE",
    "android.permission.CALL_PHONE",
    "android.permission.READ_CALL_LOG",
    "android.permission.WRITE_CALL_LOG",
    "android.permission.ADD_VOICEMAIL",
    "android.permission.PROCESS_OUTGOING_CALLS",
    "android.permission.POST_NOTIFICATIONS",
    "android.permission.VIBRATE",
    "android.permission.SCHEDULE_EXACT_ALARM",
]


def grant_permissions(driver, app_id):
    out = driver.execute_script("mobile: shell", {"command": "dumpsys package " + app_id, "args": []})
    # Find all lines that start with "   Permission "
    permissions = [line for line in out.split("\n") if line.startswith("  Permission ")]
    # Slice "  Permission " off of the beginning of each line
    permissions = [permission[13:] for permission in permissions]
    # Slice it from the beginning bracket to the next closing bracket []
    permissions = [permission[1:permission.index("]")] for permission in permissions]
    # Finally, combine the common permissions with the permissions that the app already has and remove duplicates.
    permissions = list(set(permissions + common_permissions))
    for permission in permissions:
        #print(permission)
        try:
            command = f"pm grant {app_id} {permission}"
            driver.execute_script("mobile: shell", {"command": command})
        except:
            pass
