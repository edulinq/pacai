"""
Reflection is the ability for a program to examine and modify its own code and structure when running.
For example, you may want to find the type of a variable or create an object without knowing its type when you write the code.
See: https://en.wikipedia.org/wiki/Reflective_programming .

This file aims to contain all the reflection necessary for this project
(as it can be confusing for students).
"""

import importlib
import typing

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
