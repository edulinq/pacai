import typing

import pacai.core.board

MARKER_TERMINAL: pacai.core.board.Marker = pacai.core.board.Marker('T')

BOARD_COL_DELIM: str = ','

class Board(pacai.core.board.Board):
    """
    A board for GridWorld.

    In addition to walls, grid worlds also have terminal states.
    These will be represented as `T-?\\d`, so a 'T' followed by the value of the terminal state,
    e.g., `T1`, `T100`, `T-5`.
    """

    def __init__(self, *args,
            additional_markers: list[str] | None = None,
            **kwargs) -> None:
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
        # GridWorld markers may have additional whitespace or repeated characters.
        # Only simple markers (not terminals) can have repeated characters.

        text = text.strip()
        if (len(text) == 0):
            text = ' '

        if (not text.startswith(MARKER_TERMINAL)):
            return super()._translate_marker(text[0], position)

        value = int(text[1:])
        self._terminal_values[position] = value

        return MARKER_TERMINAL

    def is_terminal_position(self, position: pacai.core.board.Position) -> bool:
        """ Check if the given position is a terminal. """

        return (position in self._terminal_values)

    def get_terminal_value(self, position: pacai.core.board.Position) -> int:
        """ Get the value of this terminal position (or raise an exception if the position is not a terminal). """

        return self._terminal_values[position]

    def get_static_text(self) -> dict[pacai.core.board.Position, str]:
        return {position: str(value) for (position, value) in self._terminal_values.items()}

    def to_dict(self) -> dict[str, typing.Any]:
        data = super().to_dict()
        data['_terminal_values'] = [(position.to_dict(), value) for (position, value) in self._terminal_values.items()]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        board = super().from_dict(data)
        board._terminal_values = {pacai.core.board.Position.from_dict(raw): value for (raw, value) in data['_terminal_values']}
        return board
