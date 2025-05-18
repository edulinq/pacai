BOOL_TRUE_STRINGS: set[str] = {
    'true', 't',
    'yes', 'y',
    '1',
}

BOOL_FALSE_STRINGS: set[str] = {
    'false', 'f',
    'no', 'n',
    '0',
}

def boolean(raw_text: str | bool) -> bool:
    """
    Parse a boolean from a string using common string representations for true/false.
    This function assumes the entire string is the boolean (not just a part of it).
    If the string is not true or false, then raise an exception.
    """

    if (isinstance(raw_text, bool)):
        return raw_text

    text = str(raw_text).lower().strip()

    if (text in BOOL_TRUE_STRINGS):
        return True

    if (text in BOOL_FALSE_STRINGS):
        return False

    raise ValueError(f"Could not convert text to boolean: '{raw_text}'.")
