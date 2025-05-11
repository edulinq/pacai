"""
This file standardizes how we write and read JSON.
Specifically, we try to be flexible when reading (using JSON5),
and strict when writing (using vanilla JSON).
"""

import abc
import enum
import json
import typing

import json5

import pacai.util.file

class DictConverter(abc.ABC):
    """
    A base class for class that can represent (serialize) and reconstruct (deserialize) themselves from a dict.
    """

    @abc.abstractmethod
    def to_dict(self) -> dict[str, typing.Any]:
        """
        Return a dict that can be used to represent this object.
        If the dict passed to from_dict(), an identical object should be reconstructed.
        """

    @classmethod
    @abc.abstractmethod
    # Note that `typing.Self` is returned, but that is introduced in Python 3.12.
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        """
        Return an instance of this subclass created using the given dict.
        If the dict came from to_dict(), the returned object should be identical to the original.
        """

def _custom_handle(obj: typing.Any) -> dict[str, typing.Any] | str:
    """
    Handle objects that are not JSON serializable by default.
    This will usually mean just calling vars() on the object.
    """

    if (isinstance(obj, DictConverter)):
        return obj.to_dict()

    if (isinstance(obj, enum.Enum)):
        return str(obj)

    if (hasattr(obj, '__dict__')):
        return vars(obj)

    raise ValueError(f"Could not JSON serialize object: '{obj}'.")

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

def load_path(path: str,
        encoding: str = pacai.util.file.DEFAULT_ENCODING,
        **kwargs) -> dict[str, typing.Any]:
    """
    Load a file path as JSON.
    If strict is set, then use standard Python JSON,
    otherwise use JSON5.
    """

    try:
        with open(path, 'r', encoding = encoding) as file:
            return load(file, **kwargs)
    except Exception as ex:
        raise ValueError(f"Failed to read JSON file '{path}'.") from ex

def loads_object(text: str, cls: typing.Type[DictConverter], **kwargs) -> DictConverter:
    """ Load a JSON string into an object (which is a subclass of DictConverter). """

    data = loads(text, **kwargs)
    return cls.from_dict(data)

def load_object_path(path: str, cls: typing.Type[DictConverter], **kwargs) -> DictConverter:
    """ Load a JSON file into an object (which is a subclass of DictConverter). """

    data = load_path(path, **kwargs)
    return cls.from_dict(data)

def dump(
        data: typing.Any,
        file_obj: typing.TextIO,
        default: typing.Callable | None = _custom_handle,
        sort_keys: bool = True,
        **kwargs) -> None:
    """ Dump an object as a JSON file object. """

    json.dump(data, file_obj, default = default, sort_keys = sort_keys, **kwargs)

def dumps(
        data: typing.Any,
        default: typing.Callable | None = _custom_handle,
        sort_keys: bool = True,
        **kwargs) -> str:
    """ Dump an object as a JSON string. """

    return json.dumps(data, default = default, sort_keys = sort_keys, **kwargs)

def dump_path(data: typing.Any,
        path: str,
        encoding: str = pacai.util.file.DEFAULT_ENCODING,
        **kwargs) -> None:
    """ Dump an object as a JSON file. """

    with open(path, 'w', encoding = encoding) as file:
        dump(data, file, **kwargs)
