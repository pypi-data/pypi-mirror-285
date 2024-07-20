import json

from test2va.const import JSON_INDENT


def write_json(data, path):
    file = open(path, "w")
    json.dump(data, file, indent=JSON_INDENT)
    file.close()
