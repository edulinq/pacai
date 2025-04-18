"""
This file standardizes how we write and read JSON files.
Specifically, we try to be flexible when reading (using JSON5),
and strict when writing (using vanilla JSON).
"""

import json

import json5

def _custom_handle(obj):
    """
    Handle objects that are not JSON serializable by default.
    This will usually mean just calling vars() on the object.
    """

    return vars(obj)

def load(file_obj, **kwargs):
    return json5.load(file_obj, **kwargs)

def loads(text, **kwargs):
    return json5.loads(text, **kwargs)

def load_path(path, **kwargs):
    try:
        with open(path, 'r') as file:
            return load(file, **kwargs)
    except Exception as ex:
        raise ValueError(f"Failed to read JSON file '{path}'.") from ex

def dump(data, file_obj, default = _custom_handle, **kwargs):
    return json.dump(data, file_obj, default = default, **kwargs)

def dumps(data, default = _custom_handle, **kwargs):
    return json.dumps(data, default = default, **kwargs)

def dump_path(data, path, **kwargs):
    with open(path, 'w') as file:
        dump(data, file, **kwargs)
