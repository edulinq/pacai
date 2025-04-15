import os
import re
import typing

import pacai.core.action
import pacai.util.file
import pacai.util.json
import pacai.util.reflection

THIS_DIR: str = os.path.join(os.path.dirname(os.path.realpath(__file__)))
BOARDS_DIR: str = os.path.join(THIS_DIR, '..', 'boards')

SEPARATOR_PATTERN: re.Pattern = re.compile(r'^\s*-{3,}\s*$')

DEFAULT_BOARD_CLASS: str = 'pacai.core.board.Board'

DEFAULT_MARKER_EMPTY: str = ' '
DEFAULT_MARKER_WALL: str = '%'

class Marker(str):
    """
    A marker represents something that can appear on a board.
    These are similar to a game piece of token in a traditional board game (like the top hat or dog in Monopoly).
    """

    pass

class Position(typing.NamedTuple):
    """
    A 2-dimension location.
    The first value represent row/y/height,
    and the second value represents col/x/width.
    """

    row: int
    """ The row / y / height of this position. """

    col: int
    """ The col / x / width of this position. """

    def to_index(self, width: int) -> int:
        """ Convert this position into a 1-dimension index. """
        return (self.row * width) + self.col

    @staticmethod
    def from_index(index: int, width: int) -> 'Position':
        """ Convert a 1-dimension index into a 2-dimension position. """
        row = index // width
        col = index % width

        return Position(row, col)

    def add(self, other: 'Position') -> 'Position':
        """
        Add another position (offset) to this one and return the result.
        """

        return Position(self.row + other.row, self.col + other.col)

class Board:
    """
    A board represents the static (non-agent) components of a game.
    For example, a board contains the walls and collectable items.

    Most types of games (anything that would subclass pacai.core.game.Game) should probably
    also subclass this to make their own type of board.

    On disk, boards are represented in files that have two sections (divided by a '---' line).
    The first section is a JSON object that holds any options for the board.
    The second section is a textual representation of the board.
    The specific board class (usually specified by the board options) should know how to interpret the text-based board.
    """

    def __init__(self,
            board_text: str,
            marker_empty: str = DEFAULT_MARKER_EMPTY,
            marker_wall: str = DEFAULT_MARKER_WALL,
            extra_markers: list[str] = [],
            strip: bool = True,
            **kwargs) -> None:
        self._marker_empty: Marker = Marker(marker_empty)
        """
        The marker used for empty locations.
        """

        self._marker_wall: Marker = Marker(marker_wall)
        """
        The marker used for wall locations.
        """

        self._markers: dict[str, Marker] = {
            marker_empty: self._marker_empty,
            marker_wall: self._marker_wall,
        }
        """ Map the text for a marker to the actual marker. """

        for marker in extra_markers:
            self._markers[marker] = Marker(marker)

        height, width, locations = self._process_text(board_text, strip = strip)

        self.height: int = height
        """ The height (number of rows, "y") of the board. """

        self.width: int = width
        """ The width (number of columns, "x") of the board. """

        self._locations: list[Marker] = locations
        """ The full content of the board as a single list. """

    def _process_text(self, board_text: str, strip: bool = True) -> tuple[int, int, list[Marker]]:
        """
        Create a board from a string.
        """

        if (strip):
            board_text = board_text.strip()

        if (len(board_text) == 0):
            raise ValueError('A board cannot be empty.')

        lines = board_text.split("\n")

        height: int = len(lines)
        width: int = -1
        locations: list[Marker] = []

        for row in range(len(lines)):
            line = lines[row]
            if (strip):
                line = line.strip()

            if (width == -1):
                width = len(line)

            if (width != len(line)):
                raise ValueError(f"Unexpected width ({len(line)}) for row at index {row}. Expected {width}.")

            for col in range(len(line)):
                marker = self._markers.get(line[col], None)
                if (marker is None):
                    raise ValueError(f"Unknown marker '{line[col]}' found at location ({row}, {col}).")

                locations.append(marker)

        if (width == 0):
            raise ValueError("A board must have at least one column.")

        return height, width, locations

    def _get_index(self, position):
        """
        Get the internal 1-d index for this position.
        Will raise if this position is not valid.
        """

        index = position.to_index(self.width)
        if ((index < 0) or (index >= len(self._locations))):
            raise ValueError("Invalid position: %s.", str(position))

        return index

    def is_wall(self, position):
        return (self._locations[self._get_index(position)] == self._marker_wall)

    def get_neighbors(self, position: Position) -> list[tuple[pacai.core.action.Action, Position]]:
        """
        Get positions that are directly touching (via cardinal directions) the given position
        without being inside a wall,
        and the action it would take to get there.
        """

        neighbors = []
        for (action, offset) in CARDINAL_OFFSETS:
            neighbor = position.add(offset)

            if ((neighbor.row < 0) or (neighbor.col < 0)):
                continue

            if ((neighbor.row >= self.height) or (neighbor.col >= self.width)):
                continue

            if (self.is_wall(neighbor)):
                continue

            neighbors.append((action, neighbor))

        return neighbors

def load_path(path: str) -> Board:
    """ Load a board from a file. """

    text = pacai.util.file.read(path, strip = False)
    return load_string(text)

def load_string(text: str) -> Board:
    """ Load a board from a string. """

    separator_index = -1
    lines = text.split("\n")

    for i in range(len(lines)):
        if (SEPARATOR_PATTERN.match(lines[i])):
            separator_index = i
            break

    if (separator_index == -1):
        # No separator was found.
        options_text = ''
        board_text = "\n".join(lines)
    else:
        options_text = "\n".join(lines[:i])
        board_text = "\n".join(lines[(i + 1):])

    options_text = options_text.strip()
    if (len(options_text) == 0):
        options = {}
    else:
        options = pacai.util.json.loads(options_text)

    board_class = options.get('class', DEFAULT_BOARD_CLASS)
    return pacai.util.reflection.new_object(board_class, board_text, **options)

CARDINAL_OFFSETS: list[tuple[pacai.core.action.Action, Position]] = [
    (pacai.core.action.NORTH, Position(-1, 0)),
    (pacai.core.action.EAST, Position(0, 1)),
    (pacai.core.action.WEST, Position(0, -1)),
    (pacai.core.action.SOUTH, Position(1, 0)),
]
