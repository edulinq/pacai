import os
import re
import typing

import pacai.core.action
import pacai.util.file
import pacai.util.json
import pacai.util.reflection

THIS_DIR: str = os.path.join(os.path.dirname(os.path.realpath(__file__)))
BOARDS_DIR: str = os.path.join(THIS_DIR, '..', 'resources', 'boards')

SEPARATOR_PATTERN: re.Pattern = re.compile(r'^\s*-{3,}\s*$')
AGENT_PATTERN: re.Pattern = re.compile(r'^\d$')

FILE_EXTENSION = '.board'

DEFAULT_BOARD_CLASS: str = 'pacai.core.board.Board'

MAX_AGENTS: int = 10

class Marker(str):
    """
    A marker represents something that can appear on a board.
    These are similar to a game pieces in a traditional board game (like the top hat or dog in Monopoly).
    Another name for this class could be "Token",
    but that term is already overloaded in Computer Science.

    Markers are used throughout the life of a game to refer to that component on the board.
    Markers may not be how a component is visually represented when the board is rendered
    (even when a board is rendered as text),
    but it will still be the identifier by which a piece is referenced.
    In a standard board, agents use the identifiers 0-9
    (and therefore there can be no more than 10 agents on a standard board).
    """

    def is_empty(self) -> bool:
        """ Check if the marker is for an empty location. """

        return (self == MARKER_EMPTY)

    def is_wall(self) -> bool:
        """ Check if the marker is for a wall. """

        return (self == MARKER_WALL)

    def is_agent(self) -> bool:
        """ Check if the marker is for an agent. """

        return (self in AGENT_MARKERS)

    def get_agent_index(self) -> int:
        """
        If this marker is an agent, return its index.
        Otherwise, return -1.
        """

        if (not self.is_agent()):
            raise ValueError(f"Marker value ('{self}') is not an agent index.")

        return int(self)

MARKER_EMPTY: Marker = Marker(' ')
"""
A marker for an empty location.
Empty markers are not stored into the board when reading from a string.
However, empty markers will be placed in grid representations of a board.
"""

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

    def apply_action(self, action: pacai.core.action.Action) -> 'Position':
        """
        Return a position that represents moving in the cardinal direction indicated by the given action.
        If the action is not one of the cardinal actions (N/E/S/W),
        then the same position will be returned.
        """

        offset = CARDINAL_OFFSETS.get(action, None)
        if (offset is None):
            return self

        return self.add(offset)

CARDINAL_DIRECTIONS: list[pacai.core.action.Action] = [
    pacai.core.action.NORTH,
    pacai.core.action.EAST,
    pacai.core.action.SOUTH,
    pacai.core.action.WEST,
]

CARDINAL_OFFSETS: dict[pacai.core.action.Action, Position] = {
    pacai.core.action.NORTH: Position(-1, 0),
    pacai.core.action.EAST: Position(0, 1),
    pacai.core.action.SOUTH: Position(1, 0),
    pacai.core.action.WEST: Position(0, -1),
}

class AdjacencyString(str):
    """
    A string that indicates which directions have something adjacent.
    This string is always four characters long,
    which each character being 'T' for true and 'F' for false.
    The characters are ordered North, East, South, West (NESW).
    So, 'TFTF' indicates that there are things to the north and south.
    """

    TRUE = 'T'
    FALSE = 'F'

    NORTH_INDEX = 0
    EAST_INDEX = 1
    SOUTH_INDEX = 2
    WEST_INDEX = 3

    def __new__(cls, raw_text: str) -> 'AdjacencyString':
        text = super().__new__(cls, raw_text.strip().upper())

        if (len(text) != 4):
            raise ValueError(f"AdjacencyString must have exactly four characters, found {len(text)}.")

        for char in text:
            if (char not in {AdjacencyString.TRUE, AdjacencyString.FALSE}):
                raise ValueError(f"AdjacencyString must only have '{AdjacencyString.TRUE}' or '{AdjacencyString.FALSE}', found '{text}'.")

        return text

    def north(self) -> bool:
        return (self[AdjacencyString.NORTH_INDEX] == AdjacencyString.TRUE)

    def east(self) -> bool:
        return (self[AdjacencyString.EAST_INDEX] == AdjacencyString.TRUE)

    def south(self) -> bool:
        return (self[AdjacencyString.SOUTH_INDEX] == AdjacencyString.TRUE)

    def west(self) -> bool:
        return (self[AdjacencyString.WEST_INDEX] == AdjacencyString.TRUE)

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

        height, width, all_objects, agents = self._process_text(board_text, strip = strip)

        self.height: int = height
        """ The height (number of rows, "y") of the board. """

        self.width: int = width
        """ The width (number of columns, "x") of the board. """

        self._all_objects: dict[Marker, set[Position]] = all_objects
        """ All the objects that appear on the board. """

        self._agent_initial_position: dict[Marker, Position] = agents
        """ Keep track of where each agent started. """

    def size(self) -> int:
        return self.height * self.width

    def agent_count(self) -> int:
        return len(self._agent_initial_position)

    def agent_indexes(self) -> list[int]:
        agent_indexes = []
        for marker in self._agent_initial_position:
            agent_indexes.append(marker.get_agent_index())

        return agent_indexes

    def get(self, position: Position) -> set[Marker]:
        """
        Get all objects at the given position.
        """

        self._check_bounds(position)

        found_objects: set[Marker] = set()
        for (marker, objects) in self._all_objects.items():
            if position in objects:
                found_objects.add(marker)

        return found_objects

    def get_marker_positions(self, marker: Marker) -> set[Position]:
        """ Get all the positions for a specific marker. """

        return self._all_objects.get(marker, set())

    def get_walls(self) -> set[Position]:
        """ Shortcut for get_marker_positions() with MARKER_WALL. """

        return self.get_marker_positions(MARKER_WALL)

    def remove_agent(self, agent_index: int) -> None:
        """
        Remove all traces of an agent from the board,
        this includes markers and initial positions.
        The agent's position will be replaces with an empty location.
        """

        if ((agent_index < 0) or (agent_index >= MAX_AGENTS)):
            return

        marker = Marker(str(agent_index))

        if (marker in self._all_objects):
            del self._all_objects[marker]

        if (marker in self._agent_initial_position):
            del self._agent_initial_position[marker]

    def remove_marker(self, marker: Marker, position: Position) -> None:
        """
        Remove the specified marker from the given position if it exists.
        """

        self._check_bounds(position)
        self._all_objects.get(marker, set()).discard(position)

    def place_marker(self, marker: Marker, position: Position) -> None:
        """
        Place a marker at the given position.
        """

        self._check_bounds(position)

        if (marker not in self._all_objects):
            self._all_objects[marker] = set()

        self._all_objects[marker].add(position)

    def get_neighbors(self, position: Position) -> list[tuple[pacai.core.action.Action, Position]]:
        """
        Get positions that are directly touching (via cardinal directions) the given position
        without being inside a wall,
        and the action it would take to get there.
        """

        neighbors = []
        for (action, offset) in CARDINAL_OFFSETS.items():
            neighbor = position.add(offset)
            if (not self._check_bounds(neighbor, throw = False)):
                continue

            if (self.is_wall(neighbor)):
                continue

            neighbors.append((action, neighbor))

        return neighbors

    def get_adjacency(self, position: Position, marker: Marker) -> AdjacencyString:
        """
        Look at the neighbors of the specified position to see if the given marker is adjacent in any direction.
        An out-of-bounds position always counts as non-adjacent.
        """

        adjacency = []
        for direction in CARDINAL_DIRECTIONS:
            neighbor = position.apply_action(direction)

            adjacent = 'F'
            if ((marker in self._all_objects) and (neighbor in self._all_objects[marker])):
                adjacent = 'T'

            adjacency.append(adjacent)

        return AdjacencyString(''.join(adjacency))

    def get_adjacent_walls(self, position: Position) -> AdjacencyString:
        """ Shortcut for get_adjacency() with MARKER_WALL. """

        return self.get_adjacency(position, MARKER_WALL)

    def is_empty(self, position: Position) -> bool:
        """ Check if the given position is empty. """

        for objects in self._all_objects.values():
            if (position in objects):
                return False

        return True

    def is_wall(self, position) -> bool:
        """ Check if the given position is a wall. """

        self._check_bounds(position)

        return (position in self._all_objects.get(MARKER_WALL, set()))

    def get_agent_position(self, agent_index: int) -> Position | None:
        """
        Get the position of an agent,
        or None if the agent is not on the board.
        """

        marker = Marker(str(agent_index))
        positions = self._all_objects.get(marker, set())

        if (len(positions) > 1):
            raise ValueError(f"Found too many agent positions ({len(positions)}) for agent {marker}. There should only be one.")

        for position in positions:
            return position

        return None

    def get_agent_initial_position(self, agent_index: int) -> Position | None:
        """
        Get the initial position of an agent,
        or None if the agent was never on the board.
        """

        marker = Marker(str(agent_index))
        return self._agent_initial_position.get(marker, None)

    def _process_text(self, board_text: str, strip: bool = True) -> tuple[int, int, dict[Marker, set[Position]], dict[Marker, Position]]:
        """
        Parse out a board from text.
        """

        if (strip):
            board_text = board_text.strip()

        if (len(board_text) == 0):
            raise ValueError('A board cannot be empty.')

        lines = board_text.split("\n")

        height: int = len(lines)
        width: int = -1
        all_objects: dict[Marker, set[Position]] = {}
        agents: dict[Marker, Position] = {}

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
                    raise ValueError(f"Unknown marker '{line[col]}' found at position ({row}, {col}).")

                if (marker.is_empty()):
                    continue

                position = Position(row, col)

                if (marker not in all_objects):
                    all_objects[marker] = set()

                all_objects[marker].add(position)

                if (marker.is_agent()):
                    if (marker in agents):
                        raise ValueError(f"Duplicate agents ('{marker}') seen on board.")

                    agents[marker] = position

        if (width == 0):
            raise ValueError("A board must have at least one column.")

        return height, width, all_objects, agents

    def to_grid(self) -> list[list[Marker]]:
        """ Convert this board to a 2-d grid. """

        grid = [[MARKER_EMPTY] * self.width for _ in range(self.height)]

        for (marker, positions) in self._all_objects.items():
            for position in positions:
                existing_marker = grid[position.row][position.col]

                # Don't replace agents.
                if (not existing_marker.is_agent()):
                    grid[position.row][position.col] = marker

        return grid

    def __str__(self) -> str:
        """ Get a rough string representation of the board. """

        grid = self.to_grid()
        return "\n".join([''.join(row) for row in grid])

    def _check_bounds(self, position: Position, throw: bool = False) -> bool:
        """
        Check if the given position is out-of-bonds for this board.
        Return True if the position is in bounds, False otherwise.
        If |throw| is True, then raise an exception.
        """

        if ((position.row < 0) or (position.col < 0) or (position.row >= self.height) or (position.col >= self.width)):
            if (throw):
                raise ValueError("Position ('%s') is out-of-bounds.", str(position))

            return False

        return True

def load_path(path: str) -> Board:
    """
    Load a board from a file.
    If the given path does not exist,
    try to prefix the path with the standard board directory and suffix with the standard extension.
    """

    raw_path = path

    # If the path does not exist, try the boards directory.
    if (not os.path.exists(path)):
        path = os.path.join(BOARDS_DIR, path)

        # If this path does not have a good extension, add one.
        if (os.path.splitext(path)[-1] != FILE_EXTENSION):
            path = path + FILE_EXTENSION

    if (not os.path.exists(path)):
        raise ValueError(f"Could not find board, path does not exist: '{raw_path}'.")

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
