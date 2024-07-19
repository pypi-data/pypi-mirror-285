import json


def print_dict(dict):
    print(json.dumps(dict, indent=4, sort_keys=True))
