import os
import re

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
    These are similar to a game piece of token in a traditional board game (like the top hat or dog in Monolopy).
    """

    pass

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
        self._markers: dict[str, Marker] = {
            marker_empty: Marker(marker_empty),
            marker_wall: Marker(marker_wall),
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
