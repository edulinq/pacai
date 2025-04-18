"""
Reflection is the ability for a program to examine and modify its own code and structure when running.
For example, you may want to find the type of a variable or create an object without knowing its type when you write the code.
See: https://en.wikipedia.org/wiki/Reflective_programming .

This file aims to contain all the reflection necessary for this project
(as it can be confusing for students).
"""

import importlib
import typing

CLASS_REF_DELIM: str = ':'

class ClassReference:
    """
    A ClassReference is constructed from a formatted that references a specific Python class.
    The basic structure of a class reference is: `[<path>:][<qualified package name>.][<module name>.]<class name>`.
    This means that a valid class reference for this class can be all of the following:
    1) `reflection.ClassReference` -- a module and class name,
    2) `pacai.util.reflection.ClassReference` -- a fully qualified name.
    3) `pacai/util/reflection.py:ClassReference` -- a path and class name,
    4) `pacai/util/reflection.py:pacai.util.reflection.ClassReference` -- a path with a fully qualified name.

    Note that a class reference without a package name will need some default package path to look in.
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

        self.filepath: str | None = filepath
        """ The filepath component of the class reference (or None). """

        self.module_name: str | None = module_name
        """ The module_name component of the class reference (or None). """

        self.class_name: str = class_name
        """ The class_name component of the class reference (or None). """

def new_object(class_name: str, *args, **kwargs) -> typing.Any:
    """
    Create a new instance of the specified class,
    passing along the args and kwargs.
    The class name should be fully qualified, e.g., 'pacai.core.agent.Agent', not just 'Agent'.

    The module must be importable (i.e., already in the PATH).
    """

    parts = class_name.split('.')
    module_name = '.'.join(parts[0:-1])
    target_name = parts[-1]

    if (len(parts) == 1):
        raise ValueError(f"Non-qualified name supplied '{class_name}'.")

    try:
        module = importlib.import_module(module_name)
    except ImportError:
        raise ValueError(f"Unable to locate module '{module_name}'.")

    target_class = getattr(module, target_name, None)
    if (target_class is None):
        raise ValueError(f"Cannot find class '{target_name}' in module '{module_name}'.")

    return target_class(*args, **kwargs)
