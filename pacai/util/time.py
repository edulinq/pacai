import time

class Duration(int):
    """
    A Duration represents some length in time in milliseconds.
    """

    def to_secs(self) -> float:
        """ Convert the duration to float seconds. """

        return self / 1000

    def to_msecs(self) -> int:
        """ Convert the duration to integer milliseconds. """

        return self

class Timestamp(int):
    """
    A Timestamp represent a moment in time (sometimes called "datetimes").
    In pacai, all times are internally represented by the number of milliseconds since the
    (Unix Epoch)[https://en.wikipedia.org/wiki/Unix_time].
    This is sometimes referred to as "Unix Time".
    """

    def sub(self, other: 'Timestamp') -> Duration:
        """ Return a new duration that is the difference of this and the given duration. """

        return Duration(self - other)

def now() -> Timestamp:
    """ Get a Timestamp that represents the current moment. """

    return Timestamp(time.time() * 1000)
