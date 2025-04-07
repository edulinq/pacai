import time

class Timestamp(int):
    """
    A Timestamp represent a moment in time (sometimes called "datetimes").
    In pacai, all times are internally represented by the number of milliseconds since the
    (Unix Epoch)[https://en.wikipedia.org/wiki/Unix_time].
    This is sometimes referred to as "Unix Time".
    """

    pass

class Duration(int):
    """
    A Duration represents some length in time in milliseconds.
    """

    pass

def now() -> Timestamp:
    return Timestamp(time.time() * 1000)
