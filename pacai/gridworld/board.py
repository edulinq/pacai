import pacai.core.board

MARKER_TERMINAL: pacai.core.board.Marker = pacai.core.board.Marker('T')

BOARD_COL_DELIM: str = ','

class Board(pacai.core.board.Board):
    """
    A board for Gridworld.

    In addition to walls, grid worlds also have terminal states.
    These will be represented as `T-?\\d`, so a 'T' followed by the value of the terminal state,
    e.g., `T1`, `T100`, `T-5`.
    """

    def __init__(self, *args, additional_markers: list[str] | None = None, **kwargs) -> None:
        if (additional_markers is None):
            additional_markers = []

        additional_markers += [
            MARKER_TERMINAL,
        ]

        kwargs['strip'] = False

        self._terminal_values: dict[pacai.core.board.Position, int] = {}
        """ Values for each terminal position. """

        super().__init__(*args, additional_markers = additional_markers, **kwargs)  # type: ignore

    def _split_line(self, line: str) -> list[str]:
        # Skip empty lines.
        if (len(line.strip()) == 0):
            return []

        return line.split(BOARD_COL_DELIM)

    def _translate_marker(self, text: str, position: pacai.core.board.Position) -> pacai.core.board.Marker | None:
        # Gridworld markers may have additional whitespace or repeated characters.
        # Only simple markers (not terminals) can have releated characters.

        text = text.strip()
        if (len(text) == 0):
            text = ' '

        if (not text.startswith(MARKER_TERMINAL)):
            return super()._translate_marker(text[0], position)

        value = int(text[1:])
        self._terminal_values[position] = value

        return MARKER_TERMINAL

    def get_static_text(self) -> dict[pacai.core.board.Position, str]:
        return {position: str(value) for (position, value) in self._terminal_values.items()}
