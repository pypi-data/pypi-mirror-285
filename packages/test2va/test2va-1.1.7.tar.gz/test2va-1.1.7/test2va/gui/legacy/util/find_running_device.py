import subprocess


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
