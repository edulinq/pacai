import edq.util.json

class SimpleComparable:
    """
    The base class for something that holds simple data and can be compared
    accurately using just it's pacai JSON representation.
    """

    def __eq__(self, other: object) -> bool:
        """
        Attempt to override the default Python `==` operator so nodes can be used in dicts and sets.
        This will not work for all subclasses, see _to_json_string().
        """

        # Note the hard type check (done so we can keep this method general).
        if (type(self) != type(other)):  # pylint: disable=unidiomatic-typecheck
            return False

        return bool(self._to_json_string() == other._to_json_string())  # type: ignore[attr-defined]

    def __hash__(self) -> int:
        """
        Attempt to override the default Python hash function so nodes can be used in dicts and sets.
        This will not work for all subclasses, see _to_json_string().
        """

        return hash(self._to_json_string())

    def __lt__(self, other: object) -> bool:
        """
        Attempt to override the default Python `<` operator so nodes can be sorted.
        This will not work for all subclasses, see _to_json_string().
        """

        # Note the hard type check (done so we can keep this method general).
        if (type(self) != type(other)):  # pylint: disable=unidiomatic-typecheck
            return False

        return bool(self._to_json_string() < other._to_json_string()) # type: ignore[attr-defined]

    def _to_json_string(self) -> str:
        """
        Attempt to convert this object into a JSON string.

        This method will generally only be used by low-level methods that are trying their best to be general.
        We want to target a string, because it has well-defined semantics for most builtin Python operations (like `==` and `<`).

        The general nature of this method will come at the cost of performance (i.e., this will be relatively slow).
        If a subclass has complex data that this method won't work on (or needs to speed things up),
        then they should implement any method in this class that uses this method
        (see comments for notes on who uses this method).
        """

        return edq.util.json.dumps(self)
