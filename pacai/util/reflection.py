"""
Reflection is the ability for a program to examine and modify its own code and structure when running.
For example, you may want to find the type of a variable or create an object without knowing its type when you write the code.
See: https://en.wikipedia.org/wiki/Reflective_programming .

This file aims to contain all the reflection necessary for this project
(as it can be confusing for students).
"""

import importlib
import importlib.util
import typing
import uuid

import pacai.util.json

REF_DELIM: str = ':'

class Reference(pacai.util.json.DictConverter):
    """
    A Reference is constructed from a formatted that references a specific Python definition (e.g. class or function).
    The rough basic structure of a reference is: `[<path>:][<qualified package name>.][<module name>.]<short name>`.
    This means that a valid reference for this class can either:
    1) `pacai.util.reflection.Reference` -- a fully qualified name.
    2) `pacai/util/reflection.py:Reference` -- a path and class name,
    """

    def __init__(self, text: str) -> None:
        """ Construct and validate a reference. """

        text = text.strip()
        if (len(text) == 0):
            raise ValueError("Cannot create a reflection reference from an empty string.")

        parts = text.split(REF_DELIM, 1)

        file_path = None
        remaining = parts[-1].strip()

        if (len(parts) > 1):
            file_path = parts[0].strip()

        if (len(remaining) == 0):
            raise ValueError("Cannot create a reflection reference without a short name.")

        parts = remaining.split('.')

        module_name = None
        short_name = parts[-1].strip()

        if (len(parts) > 1):
            module_name = '.'.join(parts[0:-1]).strip()

        if ((file_path is not None) and (module_name is not None)):
            raise ValueError(f"Cannot specify both a file path and module name for reflection reference: '{text}'.")

        if ((file_path is None) and (module_name is None)):
            raise ValueError(f"Cannot specify a short name alone, need a file_path or module name for reflection reference: '{text}'.")

        self.file_path: str | None = file_path
        """ The file_path component of the reflection reference (or None). """

        self.module_name: str | None = module_name
        """ The module_name component of the reflection reference (or None). """

        self.short_name: str = short_name
        """ The short_name component of the reflection reference (or None). """

    def __str__(self) -> str:
        return Reference.build_string(self.short_name, self.file_path, self.module_name)

    @staticmethod
    def build_string(short_name: str, file_path: str | None, module_name: str | None) -> str:
        """
        Build a string representation from the given components.
        The output should be able to be used as an argument to construct a Reference.
        """

        text = short_name

        if (module_name is not None):
            text = module_name + '.' + text

        if (file_path is not None):
            text = file_path + REF_DELIM + text

        return text

    def to_dict(self) -> dict[str, typing.Any]:
        return vars(self).copy()

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        text = Reference.build_string(data.get('short_name', ''), data.get('file_path', None), data.get('module_name', None))
        return cls(text)

def fetch(reference: Reference | str) -> typing.Any:
    """ Fetch the target of the reference. """

    if (isinstance(reference, str)):
        reference = Reference(reference)

    module = _import_module(reference)

    target = getattr(module, reference.short_name, None)
    if (target is None):
        raise ValueError(f"Cannot find target '{reference.short_name}' in reflection reference '{reference}'.")

    return target

def new_object(reference: Reference | str, *args, **kwargs) -> typing.Any:
    """
    Create a new instance of the specified class,
    passing along the args and kwargs.
    """

    target_class = fetch(reference)
    return target_class(*args, **kwargs)

def _import_module(reference):
    """
    Import and return the module for the given reflection reference.
    This may involve importing files.
    """

    # Load from a path.
    if (reference.file_path is not None):
        temp_module_name = str(uuid.uuid4()).replace('-', '')
        spec = importlib.util.spec_from_file_location(temp_module_name, reference.file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    # Load from a module name.
    try:
        return importlib.import_module(reference.module_name)
    except ImportError as ex:
        raise ValueError(f"Unable to locate module '{reference.module_name}'.") from ex
