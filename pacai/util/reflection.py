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

REF_DELIM: str = ':'

class Reference:
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

        filepath = None
        remaining = parts[-1].strip()

        if (len(parts) > 1):
            filepath = parts[0].strip()

        if (len(remaining) == 0):
            raise ValueError("Cannot create a reflection reference without a short name.")

        parts = remaining.split('.')

        module_name = None
        short_name = parts[-1].strip()

        if (len(parts) > 1):
            module_name = '.'.join(parts[0:-1]).strip()

        if ((filepath is not None) and (module_name is not None)):
            raise ValueError("Cannot specify both a filepath and module name for reflection reference: '%s'.", text)

        if ((filepath is None) and (module_name is None)):
            raise ValueError("Cannot specify a short name alone, need a filepath or module name for reflection reference: '%s'.", text)

        self.filepath: str | None = filepath
        """ The filepath component of the reflection reference (or None). """

        self.module_name: str | None = module_name
        """ The module_name component of the reflection reference (or None). """

        self.short_name: str = short_name
        """ The short_name component of the reflection reference (or None). """

    def __str__(self) -> str:
        text = self.short_name

        if (self.module_name is not None):
            text = self.module_name + '.' + text

        if (self.filepath is not None):
            text = self.filepath + REF_DELIM + text

        return text

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

    if (reference.filepath is not None):
        temp_module_name = str(uuid.uuid4()).replace('-', '')
        spec = importlib.util.spec_from_file_location(temp_module_name, reference.filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    else:
        try:
            return importlib.import_module(reference.module_name)
        except ImportError:
            raise ValueError(f"Unable to locate module '{reference.module_name}'.")
