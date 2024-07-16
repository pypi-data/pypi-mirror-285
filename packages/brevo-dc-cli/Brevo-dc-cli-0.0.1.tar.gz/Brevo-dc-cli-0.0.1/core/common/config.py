import json
import os


def get_config():
    dir_name = os.path.expanduser("~/.dt-cli")
    config = os.path.join(dir_name, "config.json")

    with open(config, "r") as f:
        data = json.load(f)

    return data


def write_config(data):
    dir_name = os.path.expanduser("~/.dt-cli")
    config = os.path.join(dir_name, "config.json")

    os.makedirs(dir_name, exist_ok=True)

    with open(config, "w") as f:
        json.dump(data, f)
