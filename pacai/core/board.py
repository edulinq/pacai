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
AGENT_PATTERN: re.Pattern = re.compile(r'^\d$')

DEFAULT_BOARD_CLASS: str = 'pacai.core.board.Board'

MAX_AGENTS: int = 10

class Marker(str):
    """
    A marker represents something that can appear on a board.
    These are similar to a game piece of token in a traditional board game (like the top hat or dog in Monopoly).
    """

    pass

MARKER_EMPTY: Marker = Marker(' ')
MARKER_WALL: Marker = Marker('%')
MARKER_AGENT_0: Marker = Marker('0')
MARKER_AGENT_1: Marker = Marker('1')
MARKER_AGENT_2: Marker = Marker('2')
MARKER_AGENT_3: Marker = Marker('3')
MARKER_AGENT_4: Marker = Marker('4')
MARKER_AGENT_5: Marker = Marker('5')
MARKER_AGENT_6: Marker = Marker('6')
MARKER_AGENT_7: Marker = Marker('7')
MARKER_AGENT_8: Marker = Marker('8')
MARKER_AGENT_9: Marker = Marker('9')

AGENT_MARKERS: set[Marker] = {
    MARKER_AGENT_0,
    MARKER_AGENT_1,
    MARKER_AGENT_2,
    MARKER_AGENT_3,
    MARKER_AGENT_4,
    MARKER_AGENT_5,
    MARKER_AGENT_6,
    MARKER_AGENT_7,
    MARKER_AGENT_8,
    MARKER_AGENT_9,
}

BASE_MARKERS: dict[str, Marker] = {
    MARKER_EMPTY: MARKER_EMPTY,
    MARKER_WALL: MARKER_WALL,
}

for agent_marker in AGENT_MARKERS:
    BASE_MARKERS[agent_marker] = agent_marker

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
    A board represents the positional components of a game.
    For example, a board contains the agents, walls and collectable items.

    Most types of games (anything that would subclass pacai.core.game.Game) should probably
    also subclass this to make their own type of board.

    On disk, boards are represented in files that have two sections (divided by a '---' line).
    The first section is a JSON object that holds any options for the board.
    The second section is a textual representation of the board.
    The specific board class (usually specified by the board options) should know how to interpret the text-based board.
    Agents on the text-based board are numbered by their index (0-9).

    Callers should generally stick to the provided methods,
    as some of the underlying data structures may be optimized for performance.
    """

    def __init__(self,
            board_text: str,
            additional_markers: list[str] = [],
            strip: bool = True,
            **kwargs) -> None:
        self._markers: dict[str, Marker] = BASE_MARKERS.copy()
        """ Map the text for a marker to the actual marker. """

        for marker in additional_markers:
            self._markers[marker] = Marker(marker)

        height, width, locations, agents = self._process_text(board_text, strip = strip)

        self.height: int = height
        """ The height (number of rows, "y") of the board. """

        self.width: int = width
        """ The width (number of columns, "x") of the board. """

        self._locations: list[Marker] = locations
        """ The full content of the board as a single list. """

        self._agents: list[int | None] = agents
        """
        Keep explicit track of each agent on this board.
        The agents are indexed by their original marker (0-9).

        A None position means that the agent is not currently on the board.

        Note that this quick lookup requires additional maintenance when agents moves.
        """

    def _process_text(self, board_text: str, strip: bool = True) -> tuple[int, int, list[Marker], list[int | None]]:
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
        agents: list[int | None] = [None] * MAX_AGENTS

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

                if (marker in AGENT_MARKERS):
                    agents[int(marker)] = (row * width) + col

                locations.append(marker)

        if (width == 0):
            raise ValueError("A board must have at least one column.")

        return height, width, locations, agents

    def _get_index(self, position):
        """
        Get the internal 1-d index for this position.
        Will raise if this position is not valid.
        """

        index = position.to_index(self.width)
        if ((index < 0) or (index >= len(self._locations))):
            raise ValueError("Invalid position: %s.", str(position))

        return index

    def move(self, old_position: Position, new_position: Position, filler: Marker = MARKER_EMPTY) -> Marker:
        """
        Move the marker from the old position to the new position.
        The previous marker at the new position will be returned,
        and the old position will be filled with the specified filler marker.
        """

        if (filler in AGENT_MARKERS):
            raise ValueError("Agents cannot be used as fillers.")

        old_index = self._get_index(old_position)
        new_index = self._get_index(new_position)

        moving_marker = self._locations[old_index]
        replaced_marker = self._locations[new_index]

        self._locations[new_index] = moving_marker
        self._locations[old_index] = filler

        # If an agent was moved or displaced, note it.
        if (replaced_marker in AGENT_MARKERS):
            agent_index = int(replaced_marker)
            self._agents[agent_index] = None

        if (moving_marker in AGENT_MARKERS):
            agent_index = int(moving_marker)
            self._agents[agent_index] = new_index

        return replaced_marker

    def is_wall(self, position):
        return (self._locations[self._get_index(position)] == MARKER_WALL)

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

    def get_agent_position(self, agent_index: int) -> Position | None:
        """
        Get the position of an agent,
        or None if the agent is not on the board.
        """

        index = self._agents[agent_index]
        if (index is None):
            return None

        return Position.from_index(index, self.width)

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
