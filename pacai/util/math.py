import math

def display_number(value: float, places: int = 2) -> str:
    """
    Format a number as a string for display purposes.
    If the value is an integer, don't use any decimal places.
    Otherwise, use the given number of places.
    """

    if (math.isclose(value, int(value))):
        return str(int(value))

    return f"%.{places}f" % (value)
