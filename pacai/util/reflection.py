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

CLASS_REF_DELIM: str = ':'

class ClassReference:
    """
    A ClassReference is constructed from a formatted that references a specific Python class.
    The rough basic structure of a class reference is: `[<path>:][<qualified package name>.][<module name>.]<class name>`.
    This means that a valid class reference for this class can either:
    1) `pacai.util.reflection.ClassReference` -- a fully qualified name.
    2) `pacai/util/reflection.py:ClassReference` -- a path and class name,
    """

    def __init__(self, text: str) -> None:
        """ Construct and validate a class reference. """

        text = text.strip()
        if (len(text) == 0):
            raise ValueError("Cannot create a class reference from an empty string.")

        parts = text.split(CLASS_REF_DELIM, 1)

        filepath = None
        remaining = parts[-1].strip()

        if (len(parts) > 1):
            filepath = parts[0].strip()

        if (len(remaining) == 0):
            raise ValueError("Cannot create a class reference without a class name.")

        parts = remaining.split('.')

        module_name = None
        class_name = parts[-1].strip()

        if (len(parts) > 1):
            module_name = '.'.join(parts[0:-1]).strip()

        if ((filepath is not None) and (module_name is not None)):
            raise ValueError("Cannot specify both a filepath and module name for class reference: '%s'.", text)

        if ((filepath is None) and (module_name is None)):
            raise ValueError("Cannot specify a class name alone, need a filepath or module name for class reference: '%s'.", text)

        self.filepath: str | None = filepath
        """ The filepath component of the class reference (or None). """

        self.module_name: str | None = module_name
        """ The module_name component of the class reference (or None). """

        self.class_name: str = class_name
        """ The class_name component of the class reference (or None). """

    def __str__(self) -> str:
        text = self.class_name

        if (self.module_name is not None):
            text = self.module_name + '.' + text

        if (self.filepath is not None):
            text = self.filepath + CLASS_REF_DELIM + text

        return text

def new_object(class_ref: ClassReference | str, *args, **kwargs) -> typing.Any:
    """
    Create a new instance of the specified class reference,
    passing along the args and kwargs.
    """

    if (isinstance(class_ref, str)):
        class_ref = ClassReference(class_ref)

    module = _import_module(class_ref)

    target_class = getattr(module, class_ref.class_name, None)
    if (target_class is None):
        raise ValueError(f"Cannot find class '{class_ref.class_name}' in class reference '{class_ref}'.")

    return target_class(*args, **kwargs)

def _import_module(class_ref):
    """
    Import and return the module for the given class reference.
    This may involve importing files.
    """

    if (class_ref.filepath is not None):
        temp_module_name = str(uuid.uuid4()).replace('-', '')
        spec = importlib.util.spec_from_file_location(temp_module_name, class_ref.filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    else:
        try:
            return importlib.import_module(class_ref.module_name)
        except ImportError:
            raise ValueError(f"Unable to locate module '{class_ref.module_name}'.")
