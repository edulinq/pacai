"""
This file standardizes how we write and read JSON.
Specifically, we try to be flexible when reading (using JSON5),
and strict when writing (using vanilla JSON).
"""

import json
import typing

import json5

def _custom_handle(obj: typing.Any) -> dict[str, typing.Any]:
    """
    Handle objects that are not JSON serializable by default.
    This will usually mean just calling vars() on the object.
    """

    return vars(obj)

def load(file_obj: typing.TextIO, strict: bool = False, **kwargs) -> dict[str, typing.Any]:
    """
    Load a file object/handler as JSON.
    If strict is set, then use standard Python JSON,
    otherwise use JSON5.
    """

    if (strict):
        return json.load(file_obj, **kwargs)

    return json5.load(file_obj, **kwargs)

def loads(text: str, strict: bool = False, **kwargs) -> dict[str, typing.Any]:
    """
    Load a string as JSON.
    If strict is set, then use standard Python JSON,
    otherwise use JSON5.
    """

    if (strict):
        return json.loads(text, **kwargs)

    return json5.loads(text, **kwargs)

def load_path(path: str, **kwargs) -> dict[str, typing.Any]:
    """
    Load a file path as JSON.
    If strict is set, then use standard Python JSON,
    otherwise use JSON5.
    """

    try:
        with open(path, 'r') as file:
            return load(file, **kwargs)
    except Exception as ex:
        raise ValueError(f"Failed to read JSON file '{path}'.") from ex

def dump(data: typing.Any, file_obj: typing.TextIO, default: typing.Callable | None = _custom_handle, **kwargs) -> None:
    """ Dump an object as a JSON file object. """

    json.dump(data, file_obj, default = default, **kwargs)

def dumps(data: typing.Any, default: typing.Callable | None = _custom_handle, **kwargs) -> None:
    """ Dump an object as a JSON string. """

    json.dumps(data, default = default, **kwargs)

def dump_path(data: typing.Any, path: str, **kwargs) -> None:
    """ Dump an object as a JSON file. """

    with open(path, 'w') as file:
        dump(data, file, **kwargs)
