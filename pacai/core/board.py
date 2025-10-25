import copy
import os
import re
import typing

import edq.util.dirent
import edq.util.json

import pacai.core.action
import pacai.util.reflection

THIS_DIR: str = os.path.join(os.path.dirname(os.path.realpath(__file__)))
BOARDS_DIR: str = os.path.join(THIS_DIR, '..', 'resources', 'boards')

SEPARATOR_PATTERN: re.Pattern = re.compile(r'^\s*-{3,}\s*$')
AGENT_PATTERN: re.Pattern = re.compile(r'^\d$')

FILE_EXTENSION = '.board'

DEFAULT_BOARD_CLASS: str = 'pacai.core.board.Board'

MAX_AGENTS: int = 10

MIN_HL_INTENSITY: int = 0
MAX_HL_INTENSITY: int = 1000

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

class Position(edq.util.json.DictConverter):
    """
    An immutable 2-dimension location
    representing row/y/height/y-offset and col/x/width/x-offset.
    """

    ROW_INDEX: int = 0
    COL_INDEX: int = 1

    MAX_SIZE: int = 1000000

    def __init__(self, row: int, col: int) -> None:
        if ((abs(row) > Position.MAX_SIZE) or (abs(col) > Position.MAX_SIZE)):
            raise ValueError(f"Dimensions {(row, col)} is greater than max of {(Position.MAX_SIZE, Position.MAX_SIZE)}.")

        self._row = row
        """ The row/y/height of this position. """

        self._col = col
        """ The col/x/width of this position. """

        self._hash: int = (row * Position.MAX_SIZE) + col
        """
        Cache the hash value to speed up checks.
        This hash value is accurate as long as the board dimensions are under one million.
        """

    @property
    def row(self) -> int:
        """ Get this position's row. """

        return self._row

    @property
    def col(self) -> int:
        """ Get this position's col. """

        return self._col

    def add(self, other: 'Position') -> 'Position':
        """
        Add another position (offset) to this one and return the result.
        """

        return Position(self._row + other._row, self._col + other._col)

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

    def __lt__(self, other: 'Position') -> bool:  # type: ignore[override]
        return (self._hash < other._hash)

    def __eq__(self, other: object) -> bool:
        if (not isinstance(other, Position)):
            return False

        return (self._hash == other._hash)

    def __hash__(self) -> int:
        return self._hash

    def __str__(self) -> str:
        return f"({self._row}, {self._col})"

    def __repr__(self) -> str:
        return str(self)

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'row': self._row,
            'col': self._col,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        return Position(row = data['row'], col = data['col'])

CARDINAL_OFFSETS: dict[pacai.core.action.Action, Position] = {
    pacai.core.action.NORTH: Position(-1, 0),
    pacai.core.action.EAST: Position(0, 1),
    pacai.core.action.SOUTH: Position(1, 0),
    pacai.core.action.WEST: Position(0, -1),
}

class Highlight(edq.util.json.DictConverter):
    """
    A class representing a request to highlight/emphasize a position on the board.
    """

    def __init__(self,
            position: Position,
            intensity: int | float | None,
            ) -> None:
        self.position = position
        """ The position of this highlight. """

        if (isinstance(intensity, float)):
            if ((intensity < 0.0) or (intensity > 1.0)):
                raise ValueError(f"Floating point highlight intensity must be in [0.0, 1.0], found: {intensity}.")

            intensity = int(intensity * MAX_HL_INTENSITY)

        if (isinstance(intensity, int)):
            if ((intensity < MIN_HL_INTENSITY) or (intensity > MAX_HL_INTENSITY)):
                raise ValueError(f"Integer highlight intensity must be in [MIN_HL_INTENSITY, MAX_HL_INTENSITY], found: {intensity}.")

        self.intensity: int | None = intensity
        """
        The highlight intensity associated with this position,
        or None if this highlight should be cleared.
        """

    def get_float_intensity(self) -> float | None:
        """ Get the highlight intensity in [0.0, 1.0]. """

        if (self.intensity is None):
            return None

        return self.intensity / MAX_HL_INTENSITY

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'position': self.position.to_dict(),
            'intensity': self.intensity,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        data = {
            'position': Position.from_dict(data['position']),
            'intensity': data['intensity'],
        }
        return cls(**data)

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
        """ Check if there is an adjacency to the north. """

        return (self[AdjacencyString.NORTH_INDEX] == AdjacencyString.TRUE)

    def east(self) -> bool:
        """ Check if there is an adjacency to the east. """

        return (self[AdjacencyString.EAST_INDEX] == AdjacencyString.TRUE)

    def south(self) -> bool:
        """ Check if there is an adjacency to the south. """

        return (self[AdjacencyString.SOUTH_INDEX] == AdjacencyString.TRUE)

    def west(self) -> bool:
        """ Check if there is an adjacency to the west. """

        return (self[AdjacencyString.WEST_INDEX] == AdjacencyString.TRUE)

class Board(edq.util.json.DictConverter):
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

    Walls are treated (and stored) specially,
    and are not expected to change once a board is created (they are considered fixed).

    Callers should generally stick to the provided methods,
    as some of the underlying data structures may be optimized for performance.
    """

    def __init__(self,
            source: str,
            board_text: str | None = None,
            markers: dict[str, Marker] | None = None,
            additional_markers: list[str] | None = None,
            strip: bool = True,
            search_target: Position | dict[str, typing.Any] | None = None,
            _height: int | None = None,
            _width: int | None = None,
            _walls: set[Position] | None = None,
            _nonwall_objects: dict[Marker, set[Position]] | None = None,
            _agent_initial_positions: dict[Marker, Position] | None = None,
            **kwargs: typing.Any) -> None:
        """
        Construct a board.
        The board details will either be parsed from `board_text` is provided,
        or taken directly from the given underscore arguments.
        """

        self.source: str = source
        """ Where this board was loaded from. """

        if (markers is None):
            markers = BASE_MARKERS.copy()

        self._markers: dict[str, Marker] = markers
        """ Map the text for a marker to the actual marker. """

        if (additional_markers is not None):
            for marker in additional_markers:
                self._markers[marker] = Marker(marker)

        self.height: int = -1
        """ The height (number of rows, "y") of the board. """

        self.width: int = -1
        """ The width (number of columns, "x") of the board. """

        self._walls: set[Position] = set()
        """ The walls for this board. """

        self._neighbor_cache: dict[Position, list[tuple[pacai.core.action.Action, Position]]]  = {}
        """
        Keep a cache of all neighbor locations.
        Note that neighbors only depend on the size of the board and walls.
        Computing neighbors is a high-throughput activity, and therefore justifies a cache.
        Neighbors will be shallow copied when a board is copied,
        therefore all successor boards will share the same cache.
        """

        self._nonwall_objects: dict[Marker, set[Position]] = {}
        """ All the non-wall objects that appear on the board. """

        self._agent_initial_positions: dict[Marker, Position] = {}
        """ Keep track of where each agent started. """

        if (isinstance(search_target, dict)):
            search_target = Position.from_dict(search_target)

        self.search_target: Position | None = search_target  # type: ignore
        """ Some boards (especially mazes) will have a specific positional search target. """

        self._is_shallow: bool = False
        """
        Keep track of if the variable components of the board have been copied.
        We will only make a copy of these component on a write.
        """

        # The board text has been provided, parse the data from it.
        if (board_text is not None):
            height, width, all_objects, agents = self._process_text(board_text, strip = strip)

            walls = set()
            if (MARKER_WALL in all_objects):
                walls = all_objects[MARKER_WALL]
                del all_objects[MARKER_WALL]

            self.height = height
            self.width = width
            self._walls = walls
            self._nonwall_objects = all_objects
            self._agent_initial_positions = agents
        else:
            # No board text has been provided, all attributes must be provided.
            checks = [
                (_height, 'height'),
                (_width, 'width'),
                (_nonwall_objects, 'objects'),
                (_agent_initial_positions, 'agent initial positions'),
            ]

            for (value, label) in checks:
                if (value is None):
                    raise ValueError(f"Board {label} cannot be empty when the board text is not supplied.")

            self.height = _height  # type: ignore
            self.width = _width  # type: ignore
            self._walls = _walls  # type: ignore
            self._nonwall_objects = _nonwall_objects  # type: ignore
            self._agent_initial_positions = _agent_initial_positions  # type: ignore

    def copy(self) -> 'Board':
        """ Get a copy of this board. """

        # Make a shallow copy.
        new_board = copy.copy(self)

        # Mark both ourself and the copy as shallow.
        self._is_shallow = True
        new_board._is_shallow = True

        return new_board

    def _copy_on_write(self) -> None:
        """ Copy any copy-on-write components if necessary. """

        if (not self._is_shallow):
            return

        self._nonwall_objects = {marker: positions.copy() for (marker, positions) in self._nonwall_objects.items()}
        self._is_shallow = False

    def size(self) -> int:
        """ Get the total number of places in this board. """

        return self.height * self.width

    def get_corners(self, offset: int = 0) -> tuple[Position, Position, Position, Position]:
        """
        Get the corner positions of this board (ordered as NE, SE, SW, NW).

        The offset is how much to move diagonally in from each corner.
        By default, it is zero and will be exactly at each corner position.
        However many board have a border of walls,
        in this case an offset of 1 will return those non-border corners.
        """

        # Add 1 for zero indexing.
        high_offset = (1 + offset)

        return (
            Position(offset, self.width - high_offset),
            Position(self.height - high_offset, self.width - high_offset),
            Position(self.height - high_offset, offset),
            Position(offset, offset),
        )

    def agent_count(self) -> int:
        """
        Return the number of agents supported by this board.
        This counts the number of initial position seen for agents when the board was first parsed.
        """

        return len(self._agent_initial_positions)

    def agent_indexes(self) -> list[int]:
        """
        Get the indexes for all the agents supposed by this board.
        The reported agents are agents supported by the board, not just agents currently on the board.
        """

        agent_indexes = []
        for marker in self._agent_initial_positions:
            agent_indexes.append(marker.get_agent_index())

        return agent_indexes

    def get(self, position: Position) -> set[Marker]:
        """
        Get all non-wall objects at the given position.
        """

        self._check_bounds(position)

        found_objects: set[Marker] = set()
        for (marker, objects) in self._nonwall_objects.items():
            if position in objects:
                found_objects.add(marker)

        return found_objects

    def get_marker_positions(self, marker: Marker) -> set[Position]:
        """ Get all the non-wall positions for a specific marker. """

        return self._nonwall_objects.get(marker, set()).copy()

    def get_marker_count(self, marker: Marker) -> int:
        """ Get a count of the non-wall positions for a specific marker. """

        return len(self._nonwall_objects.get(marker, []))

    def get_walls(self) -> set[Position]:
        """ Get all the walls. """

        return self._walls

    def remove_agent(self, agent_index: int) -> None:
        """
        Remove all traces of an agent from the board,
        this includes markers and initial positions.
        The agent's position will be replaces with an empty location.
        """

        if ((agent_index < 0) or (agent_index >= MAX_AGENTS)):
            return

        self._copy_on_write()

        marker = Marker(str(agent_index))

        if (marker in self._nonwall_objects):
            del self._nonwall_objects[marker]

        if (marker in self._agent_initial_positions):
            del self._agent_initial_positions[marker]

    def remove_marker(self, marker: Marker, position: Position) -> None:
        """
        Remove the specified marker from the given position if it exists.
        """

        self._check_bounds(position)
        self._copy_on_write()

        markers = self._nonwall_objects.get(marker)
        if (markers is None):
            return

        markers.discard(position)

    def place_marker(self, marker: Marker, position: Position) -> None:
        """
        Place a marker at the given position.
        """

        self._check_bounds(position)
        self._copy_on_write()

        if (marker not in self._nonwall_objects):
            self._nonwall_objects[marker] = set()

        self._nonwall_objects[marker].add(position)

    def get_neighbors(self, position: Position) -> list[tuple[pacai.core.action.Action, Position]]:
        """
        Get positions that are directly touching (via cardinal directions) the given position
        without being inside a wall,
        and the action it would take to get there.

        Note that this is a high-throughput piece of code, and may contain optimizations.
        """

        # Check the neighbor cache.
        if (position in self._neighbor_cache):
            return self._neighbor_cache[position]

        neighbors = []
        for (action, offset) in CARDINAL_OFFSETS.items():
            neighbor = position.add(offset)

            if (not self._check_bounds(neighbor, throw = False)):
                continue

            if (self.is_wall(neighbor)):
                continue

            neighbors.append((action, neighbor))

        # Save to the neighbor cache.
        self._neighbor_cache[position] = neighbors

        return neighbors

    def get_adjacency(self, position: Position, marker: Marker) -> AdjacencyString:
        """
        Look at the neighbors of the specified position to see if the given marker is adjacent in any direction.
        An out-of-bounds position always counts as non-adjacent.
        """

        # Get the set of positions to compare against.
        if (marker == MARKER_WALL):
            positions = self._walls
        else:
            positions = self._nonwall_objects[marker]

        adjacency = []
        for direction in pacai.core.action.CARDINAL_DIRECTIONS:
            neighbor = position.apply_action(direction)

            adjacent = 'F'
            if (neighbor in positions):
                adjacent = 'T'

            adjacency.append(adjacent)

        return AdjacencyString(''.join(adjacency))

    def get_adjacent_walls(self, position: Position) -> AdjacencyString:
        """ Shortcut for get_adjacency() with MARKER_WALL. """

        return self.get_adjacency(position, MARKER_WALL)

    def is_empty(self, position: Position) -> bool:
        """ Check if the given position is empty. """

        for objects in self._nonwall_objects.values():
            if (position in objects):
                return False

        return (position not in self._walls)

    def is_marker(self, marker: Marker, position: Position) -> bool:
        """ Check if the given position is has the target marker. """

        # Get the set of positions to compare against.
        if (marker == MARKER_WALL):
            positions = self._walls
        else:
            positions = self._nonwall_objects[marker]

        return (position in positions)

    def is_wall(self, position: Position) -> bool:
        """ Check if the given position is a wall. """

        # Note that we are not using is_marker() for a slight speedup (since this is a common method).
        return (position in self._walls)

    def get_agent_position(self, agent_index: int) -> Position | None:
        """
        Get the position of an agent,
        or None if the agent is not on the board.
        """

        marker = Marker(str(agent_index))
        positions = self._nonwall_objects.get(marker, set())

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
        return self._agent_initial_positions.get(marker, None)

    def get_nonwall_string(self) -> str:
        """
        Get a string representation of the non-wall objects on the board.
        This should not be used for any performant code,
        but provides a consistent way of identifying the "state" of the board.
        """

        raw_nonwall_objects = []
        for (marker, positions) in sorted(self._nonwall_objects.items()):
            raw_nonwall_objects.append(f"{marker}::{','.join([str(position) for position in sorted(positions)])}")

        return '||'.join(raw_nonwall_objects)

    def to_grid(self) -> list[list[Marker]]:
        """ Convert this board to a 2-d grid. """

        grid = [[MARKER_EMPTY] * self.width for _ in range(self.height)]

        # Place walls first.
        for position in self._walls:
            grid[position.row][position.col] = MARKER_WALL

        # Place non-agents.
        for (marker, positions) in self._nonwall_objects.items():
            if (marker.is_agent()):
                continue

            for position in positions:
                grid[position.row][position.col] = marker

        # Place agents.
        for (marker, positions) in self._nonwall_objects.items():
            if (not marker.is_agent()):
                continue

            for position in positions:
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
                raise ValueError(f"Position ('{str(position)}') is out-of-bounds.")

            return False

        return True

    def to_dict(self) -> dict[str, typing.Any]:
        all_objects = {}
        for (marker, positions) in sorted(self._nonwall_objects.items()):
            all_objects[str(marker)] = [position.to_dict() for position in sorted(positions)]

        agent_initial_positions = {}
        for (marker, position) in sorted(self._agent_initial_positions.items()):
            agent_initial_positions[str(marker)] = position.to_dict()

        search_target: Position | dict[str, typing.Any] | None = self.search_target
        if (isinstance(search_target, Position)):
            search_target = search_target.to_dict()

        return {
            'source': self.source,
            'markers': {key: str(marker) for (key, marker) in sorted(self._markers.items())},
            'height': self.height,
            'width': self.width,
            'search_target': search_target,
            '_walls': [position.to_dict() for position in sorted(self._walls)],
            '_nonwall_objects': all_objects,
            '_agent_initial_positions': agent_initial_positions,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        all_objects: dict[Marker, set[Position]] = {}
        for (raw_marker, raw_positions) in data['_nonwall_objects'].items():
            all_objects[Marker(raw_marker)] = {Position.from_dict(raw_position) for raw_position in raw_positions}

        agent_initial_positions = {}
        for (raw_marker, raw_position) in data['_agent_initial_positions'].items():
            agent_initial_positions[Marker(raw_marker)] = Position.from_dict(raw_position)

        search_target = data.get('search_target', None)
        if (search_target is not None):
            search_target = Position.from_dict(search_target)

        return cls(
            source = data['source'],
            markers = {key: Marker(marker) for (key, marker) in data['markers'].items()},
            search_target = search_target,
            _height = data['height'],
            _width = data['width'],
            _walls = {Position.from_dict(raw_position) for raw_position in data.get('_walls', [])},
            _nonwall_objects = all_objects,
            _agent_initial_positions = agent_initial_positions,
        )

    def _process_text(self,
            board_text: str,
            strip: bool = True,
            ) -> tuple[int, int, dict[Marker, set[Position]], dict[Marker, Position]]:
        """
        Parse out a board from text.
        """

        if (strip):
            board_text = board_text.strip()

        if (len(board_text) == 0):
            raise ValueError('A board cannot be empty.')

        lines = board_text.split("\n")

        width: int = -1
        all_objects: dict[Marker, set[Position]] = {}
        agents: dict[Marker, Position] = {}

        row_skip_count = 0
        for (raw_row, line) in enumerate(lines):
            row = raw_row - row_skip_count

            if (strip):
                line = line.strip()

            raw_markers = self._split_line(line)

            # Skip empty lines.
            if (len(raw_markers) == 0):
                row_skip_count += 1
                continue

            if (width == -1):
                width = len(raw_markers)

            if (width != len(raw_markers)):
                raise ValueError(f"Unexpected width ({len(raw_markers)}) for row at index {row}. Expected {width}.")

            for (col, raw_marker) in enumerate(raw_markers):
                position = Position(row, col)

                marker = self._translate_marker(raw_marker, position)
                if (marker is None):
                    raise ValueError(f"Unknown marker '{raw_marker}' found at position ({row}, {col}).")

                if (marker.is_empty()):
                    continue

                if (marker not in all_objects):
                    all_objects[marker] = set()

                all_objects[marker].add(position)

                if (marker.is_agent()):
                    if (marker in agents):
                        raise ValueError(f"Duplicate agents ('{marker}') seen on board.")

                    agents[marker] = position

        if (width <= 0):
            raise ValueError("A board must have at least one column.")

        height: int = len(lines) - row_skip_count

        return height, width, all_objects, agents

    def _split_line(self, line: str) -> list[str]:
        """
        Split a line in the text representation of a board.
        By default, this just splits into characters.
        """

        return list(line)

    def _translate_marker(self, text: str, position: Position) -> Marker | None:
        """
        Translate the given text into the correct marker.
        By default, this just looks up the text in self._markers.
        """

        return self._markers.get(text, None)

def load_path(path: str, **kwargs: typing.Any) -> Board:
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

    text = edq.util.dirent.read_file(path, strip = False)
    return load_string(raw_path, text, **kwargs)

def load_string(source: str, text: str, **kwargs: typing.Any) -> Board:
    """ Load a board from a string. """

    separator_index = -1
    lines = text.split("\n")

    for (i, line) in enumerate(lines):
        if (SEPARATOR_PATTERN.match(line)):
            separator_index = i
            break

    if (separator_index == -1):
        # No separator was found.
        options_text = ''
        board_text = "\n".join(lines)
    else:
        options_text = "\n".join(lines[:separator_index])
        board_text = "\n".join(lines[(separator_index + 1):])

    options_text = options_text.strip()
    if (len(options_text) == 0):
        options = {}
    else:
        options = edq.util.json.loads(options_text)

    options.update(kwargs)

    board_class = options.get('class', DEFAULT_BOARD_CLASS)
    return pacai.util.reflection.new_object(board_class, source, board_text, **options)  # type: ignore[no-any-return]

def create_empty(source: str, height: int, width: int, **kwargs: typing.Any) -> Board:
    """
    Create an empty board with the given dimensions.
    """

    text = ((MARKER_EMPTY * width) + "\n") * height
    return load_string(source, text, strip = False)
