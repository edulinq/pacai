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

_cache: dict[str, typing.Any] = {}
"""
A cache to help avoid importing a module multiple times.
The key is the string representation of a reference.
"""

class Reference(pacai.util.json.DictConverter):
    """
    A Reference is constructed from a formatted that references a specific Python definition (e.g. class or function).
    The rough basic structure of a reference is: `[<path>:][<qualified package name>.][<module name>.]<short name>`.
    This means that a valid reference for this class can either:
    1) `pacai.util.reflection.Reference` -- a fully qualified name.
    2) `pacai/util/reflection.py:Reference` -- a path and class name,
    """

    def __init__(self,
            raw_input: typing.Union[str, 'Reference'],
            check_alias: bool = True,
            ) -> None:
        """ Construct and validate a reference. """

        if (isinstance(raw_input, Reference)):
            file_path = raw_input.file_path
            module_name = raw_input.module_name
            short_name = raw_input.short_name
        else:
            file_path, module_name, short_name = Reference.parse_string(raw_input, check_alias)

        self.file_path: str | None = file_path
        """ The file_path component of the reflection reference (or None). """

        self.module_name: str | None = module_name
        """ The module_name component of the reflection reference (or None). """

        self.short_name: str = short_name
        """ The short_name component of the reflection reference (or None). """

    def __str__(self) -> str:
        return Reference.build_string(self.short_name, self.file_path, self.module_name)

    def __repr__(self) -> str:
        return str(self)

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

    @staticmethod
    def parse_string(text: str, check_alias: bool = True) -> tuple[str | None, str | None, str]:
        """ Parse out the key reference components from a string. """

        text = text.strip()
        if (len(text) == 0):
            raise ValueError("Cannot parse a reflection reference from an empty string.")

        # Check if this looks like an alias.
        if (check_alias and ('.' not in text)):
            text = pacai.util.alias.lookup(text, text)

        parts = text.rsplit(REF_DELIM, 1)

        file_path = None
        remaining = parts[-1].strip()

        if (len(parts) > 1):
            file_path = parts[0].strip()

        if (len(remaining) == 0):
            raise ValueError("Cannot parse a reflection reference without a short name.")

        parts = remaining.split('.')

        module_name = None
        short_name = parts[-1].strip()

        if (len(parts) > 1):
            module_name = '.'.join(parts[0:-1]).strip()

        if ((file_path is not None) and (module_name is not None)):
            raise ValueError(f"Cannot specify both a file path and module name for reflection reference: '{text}'.")

        if ((file_path is None) and (module_name is None)):
            raise ValueError(f"Cannot specify a (non-alias) short name alone, need a file_path or module name for reflection reference: '{text}'.")

        return file_path, module_name, short_name

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

T = typing.TypeVar('T')

def resolve_and_fetch(
        cls: typing.Type,
        raw_object: T | Reference | str,
        ) -> typing.Any:
    """
    Resolve the given raw object into the specified class.
    If it is already an object of that type, just return it.
    If it is a reference or string, resolve the reference and fetch the reference.
    """

    if (isinstance(raw_object, cls)):
        return raw_object

    reference = Reference(typing.cast(Reference | str, raw_object))
    result = fetch(reference)

    if (not isinstance(result, cls)):
        raise ValueError(f"Target '{reference}' is not of type '{cls}', found type '{type(result)}'.")

    return result

def _import_module(reference):
    """
    Import and return the module for the given reflection reference.
    This may involve importing files.
    """

    reference_string = str(reference)

    # Check the cache before importing.
    module = _cache.get(reference_string, None)
    if (module is not None):
        return module

    # Load from a path.
    if (reference.file_path is not None):
        temp_module_name = str(uuid.uuid4()).replace('-', '')
        spec = importlib.util.spec_from_file_location(temp_module_name, reference.file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    else:
        # Load from a module name.
        try:
            module = importlib.import_module(reference.module_name)
        except ImportError as ex:
            raise ValueError(f"Unable to locate module '{reference.module_name}'.") from ex

    # Store the module in the cache.
    _cache[reference_string] = module

    return module

def get_qualified_name(target: type | object | Reference | str) -> str:
    """
    Try to get a qualified name for a type (or for the type of an object).
    Names will not always come out clean.
    """

    # If this is a string or reference, just resolve the reference.
    if (isinstance(target, (Reference, str))):
        return str(Reference(target))

    # Get the type for this target.
    if (isinstance(target, type)):
        target_class = target
    elif (callable(target)):
        target_class = typing.cast(type, target)
    else:
        target_class = type(target)

    # Check for various name components.
    parts = []

    if (hasattr(target_class, '__module__')):
        parts.append(str(getattr(target_class, '__module__')))

    if (hasattr(target_class, '__qualname__')):
        parts.append(str(getattr(target_class, '__qualname__')))
    elif (hasattr(target_class, '__name__')):
        parts.append(str(getattr(target_class, '__name__')))

    # Fall back to just the string reprsentation.
    if (len(parts) == 0):
        return str(target_class)

    return '.'.join(parts)
