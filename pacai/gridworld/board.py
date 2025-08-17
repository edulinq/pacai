import typing

import pacai.core.board

MARKER_TERMINAL: pacai.core.board.Marker = pacai.core.board.Marker('T')
MARKER_DISPLAY_VALUE: pacai.core.board.Marker = pacai.core.board.Marker('V')
MARKER_DISPLAY_QVALUE: pacai.core.board.Marker = pacai.core.board.Marker('Q')
MARKER_SEPARATOR: pacai.core.board.Marker = pacai.core.board.Marker('X')

AGENT_MARKER: pacai.core.board.Marker = pacai.core.board.MARKER_AGENT_0
""" The fixed marker of the only agent. """

BOARD_COL_DELIM: str = ','

class Board(pacai.core.board.Board):
    """
    A board for GridWorld.

    In addition to walls, grid worlds also have terminal states.
    These will be represented as `T-?\\d`, so a 'T' followed by the value of the terminal state,
    e.g., `T1`, `T100`, `T-5`.
    """

    def __init__(self, *args: typing.Any,
            additional_markers: list[str] | None = None,
            qdisplay: bool = False,
            **kwargs: typing.Any) -> None:
        """
        Construct a GridWorld board.
        If qdisplay is true, then the existing board will be extended to display Q-Values and policies.
        """

        if (additional_markers is None):
            additional_markers = []

        additional_markers += [
            MARKER_TERMINAL,
        ]

        kwargs['strip'] = False

        self._terminal_values: dict[pacai.core.board.Position, int] = {}
        """ Values for each terminal position. """

        # Ensure that super's init() is called after self._terminal_values exists.
        super().__init__(*args, additional_markers = additional_markers, **kwargs)  # type: ignore

        self._original_height: int = self.height
        """ The original height for this board. """

        self._original_width: int = self.width
        """ The original width for this board. """

        if (qdisplay):
            self._add_qvalue_display()

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

    def display_qvalues(self) -> bool:
        """ Check if this board is displaying Q-Values. """

        return len(self.get_marker_positions(MARKER_SEPARATOR)) > 0

    def _add_qvalue_display(self) -> None:
        """
        Add a Q-Value display, which includes a section for values and q-values.
        The board will be doubled in size (along each dimension).
        The top-left will have the original board (with agent),
        the top-right will have the values and policies,
        and the bottom-left will have the q-values.
        """

        if (len(self.get_marker_positions(MARKER_SEPARATOR)) > 0):
            raise ValueError("Already added Q-Value display.")

        self._original_height = self.height
        self._original_width = self.width
        base_walls = self._walls.copy()

        # Grow the board.
        self.height = (self._original_height * 2) + 1
        self.width = (self._original_width * 2) + 1

        offset_values = pacai.core.board.Position(0, self._original_width + 1)  # Values (Top-Right)
        offset_qvalues = pacai.core.board.Position(self._original_height + 1, 0)  # Q-Values (Bottom-Left)

        # Add separators to quarter off sections of the new board.

        for row in range(self.height):
            self.place_marker(MARKER_SEPARATOR, pacai.core.board.Position(row, self._original_width))

        for col in range(self.width):
            self.place_marker(MARKER_SEPARATOR, pacai.core.board.Position(self._original_height, col))

        # Empty out the blank section.
        for row in range(self._original_height):
            for col in range(self._original_width):
                position = pacai.core.board.Position(self._original_height + 1 + row, self._original_width + 1 + col)
                self.place_marker(MARKER_SEPARATOR, position)

        # Duplicate the walls on the new sections.

        for offset in [offset_values, offset_qvalues]:
            for base_wall in base_walls:
                self._walls.add(base_wall.add(offset))

        # Place the markers to display values/q-values.

        for base_row in range(self._original_height):
            for base_col in range(self._original_width):
                base_position = pacai.core.board.Position(base_row, base_col)
                if (self.is_wall(base_position) or self.is_marker(MARKER_TERMINAL, base_position)):
                    continue

                self.place_marker(MARKER_DISPLAY_VALUE, base_position.add(offset_values))
                self.place_marker(MARKER_DISPLAY_QVALUE, base_position.add(offset_qvalues))

        # Copy terminal markers.

        for (base_position, value) in list(self._terminal_values.items()):
            for offset in [offset_values, offset_qvalues]:
                position = base_position.add(offset)
                self._terminal_values[position] = value
                self.place_marker(MARKER_TERMINAL, position)

    def to_dict(self) -> dict[str, typing.Any]:
        data = super().to_dict()
        data['_terminal_values'] = [(position.to_dict(), value) for (position, value) in self._terminal_values.items()]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        board = super().from_dict(data)
        board._terminal_values = {pacai.core.board.Position.from_dict(raw): value for (raw, value) in data['_terminal_values']}
        return board
