import argparse
import logging
import random
import sys
import typing

import pacai.core.board
import pacai.core.log
import pacai.pacman.board
import pacai.util.reflection

MIN_SIZE: int = 10

MAX_RANDOM_SIZE: int = 24
""" The maximum size for a maze with unspecified size. """

MIN_MAZE_AXIS_WIDTH: int = 1

DEFAULT_GAPS: int = 3

DEFAULT_GAP_FACTOR: float = 0.50
MAX_GAP_FACTOR: float = 0.65
GAP_FACTOR_STDEV: float = 0.1

MAX_PRISON_WIDTH: int = 3

MIN_PELLETS: int = 1
MAX_PELLETS: int = 100

MIN_CAPSULES: int = 0
MAX_CAPSULES: int = 4

DEFAULT_NUM_AGENTS: int = 2

class Maze:
    """
    A recursive definition of a maze.

    Each maze has an "anchor", which is the position of its top-left (northwest) corner in it's parent.
    There is only one collection of markers that backs all mazes in a tree.
    """

    def __init__(self,
            height: int, width: int,
            anchor: pacai.core.board.Position | None = None, root: typing.Union['Maze', None] = None,
            prison_width: int = 0,
            ) -> None:
        self.height: int = height
        """ The height of this submaze. """

        self.width: int = width
        """ The width of this submaze. """

        if (anchor is None):
            anchor = pacai.core.board.Position(0, 0)

        self.anchor: pacai.core.board.Position = anchor
        """ The position that this maze lives at according to the root/parent maze. """

        grid = None

        if (root is None):
            root = self
        else:
            grid = root.grid

        self.root: 'Maze' = root
        """
        The parent of this maze (the maze that this (sub)maze lives inside).
        The true root will have itself as a parent.
        """

        if (grid is None):
            grid = [[pacai.core.board.MARKER_EMPTY for col in range(width)] for row in range(height)]

        self.grid: list[list[pacai.core.board.Marker]] = grid
        """
        A 2-dimensional representation of all the markers in this maze.
        All mazes in this tree will share the same grid.
        """

        if (len(self.grid) == 0):
            raise ValueError("Grid cannot have a zero height.")

        self.submazes: list['Maze'] = []
        """ The submazes/children in this maze. """

        self.prison_width: int = prison_width
        """
        The number of columns used by the "prisons".
        Prisons are the starting areas for each agent.
        This number does not include walls.
        """

    def place_relative(self, row: int, col: int, marker: pacai.core.board.Marker) -> None:
        """ Place a marker in the grid according to the relative coordinates of this submaze. """

        self.grid[self.anchor.row + row][self.anchor.col + col] = marker

    def is_marker_relative(self, row: int, col: int, marker: pacai.core.board.Marker) -> bool:
        """ Check if the given marker exists at the relative coordinates of this submaze. """

        true_row = self.anchor.row + row
        true_col = self.anchor.col + col

        # No markers are out-of-bounds.
        if ((true_row < 0) or (true_row >= len(self.grid)) or (true_col < 0) or (true_col >= len(self.grid[0]))):
            return False

        return (self.grid[true_row][true_col] == marker)

    def to_board(self, source: str) -> pacai.core.board.Board:
        """
        Create a pacai capture board from this maze.
        This will add a border (of walls), add a mirrored copy (for the other team), and properly set agent indexes.
        """

        # Make a new grid that is big enough to include the opposing side (mirrored) and a border (wall) around the entire board.
        # Initialize with wall markers for the boarder.
        new_grid = [[pacai.core.board.MARKER_WALL for col in range((self.width * 2) + 2)] for row in range(self.height + 2)]

        for base_row in range(self.height):
            for base_col in range(self.width):
                # Offset for the boarder.
                row = base_row + 1
                col = base_col + 1

                # Copy the left side, and mirror around both axes for the right side.

                copy_marker = self.grid[base_row][base_col]
                mirror_marker = self.grid[self.height - base_row - 1][self.width - base_col - 1]

                # If either marker is an agent, adjust the indexes.
                # Even (including 0) are on the left, and odds are on the right.

                if (copy_marker.is_agent()):
                    copy_marker = pacai.core.board.Marker(str(copy_marker.get_agent_index() * 2))

                if (mirror_marker.is_agent()):
                    mirror_marker = pacai.core.board.Marker(str((mirror_marker.get_agent_index() * 2) + 1))

                # Place the final markers.
                new_grid[row][col] = copy_marker
                new_grid[row][col + self.width] = mirror_marker

        board_text = "\n".join([''.join(row) for row in new_grid])

        kwargs = {
            'strip': False,
            'class': pacai.util.reflection.get_qualified_name(pacai.pacman.board.Board),
        }

        return pacai.core.board.load_string(source, board_text, **kwargs)

    def _add_wall(self, rng: random.Random, wall_index: int, gaps: float = 1.0, vertical: bool = True) -> bool:
        """
        Try to add a vertical wall with gaps at the given location.
        Return True if a wall was added, False otherwise.
        """

        if (vertical):
            return self._add_vertical_wall(rng, wall_index, gaps = gaps)

        return self._add_horizontal_wall(rng, wall_index, gaps = gaps)

    def _add_vertical_wall(self, rng: random.Random, col: int, gaps: float = 1.0) -> bool:
        """
        Try to add a vertical wall with gaps at the given col.
        Return True if a wall was added, False otherwise.
        """

        # Choose the specific number of gaps we are expecting.
        gaps = int(round(min(self.height, gaps)))

        # The places (rows) that we may put a wall.
        slots = list(range(self.height))

        # If there are empty spaces directly above or below our proposed wall,
        # then don't put a wall marker directly in front of those respective spaces.
        # This prevents us blocking entrances into our submaze.

        if (self.is_marker_relative(-1, col, pacai.core.board.MARKER_EMPTY)):
            slots.remove(0)

        if (len(slots) == 0):
            return False

        if (self.is_marker_relative(self.height, col, pacai.core.board.MARKER_EMPTY)):
            slots.remove(self.height - 1)

        # If we cannot provided the requested number of gaps, then don't put down the wall.
        if (len(slots) <= gaps):
            return False

        # Randomize where we will put our walls.
        rng.shuffle(slots)

        # Skip the first slots (these are gaps), and place the rest.
        for row in slots[gaps:]:
            self.place_relative(row, col, pacai.core.board.MARKER_WALL)

        # By placing a wall, we have created two new submazes (on each side of the wall).

        # One submaze to the left.
        self.submazes.append(Maze(self.height, col, anchor = self.anchor, root = self.root))

        # One submaze to the right.
        anchor_offset = pacai.core.board.Position(0, col + 1)
        self.submazes.append(Maze(self.height, (self.width - col - 1), self.anchor.add(anchor_offset), self.root))

        return True

    def _add_horizontal_wall(self, rng: random.Random, row: int, gaps: float = 1.0) -> bool:
        """
        Try to add a horizontal wall with gaps at the given row.
        Return True if a wall was added, False otherwise.
        """

        # Choose the specific number of gaps we are expecting.
        discrete_gaps = int(round(min(self.width, gaps)))

        # The places (cols) that we may put a wall.
        slots = list(range(self.width))

        # If there are empty spaces directly to the left/right of our proposed wall,
        # then don't put a wall marker directly in front of those respective spaces.
        # This prevents us blocking entrances into our submaze.

        if (self.is_marker_relative(row, -1, pacai.core.board.MARKER_EMPTY)):
            slots.remove(0)

        if (len(slots) == 0):
            return False

        if (self.is_marker_relative(row, self.width, pacai.core.board.MARKER_EMPTY)):
            slots.remove(self.width - 1)

        # If we cannot provided the requested number of gaps, then don't put down the wall.
        if (len(slots) <= discrete_gaps):
            return False

        # Randomize where we will put our walls.
        rng.shuffle(slots)

        # Skip the first slots (these are gaps), and place the rest.
        for col in slots[discrete_gaps:]:
            self.place_relative(row, col, pacai.core.board.MARKER_WALL)

        # By placing a wall, we have created two new submazes (on each side of the wall).

        # One submaze above.
        self.submazes.append(Maze(row, self.width, anchor = self.anchor, root = self.root))

        # One submaze below.
        anchor_offset = pacai.core.board.Position(row + 1, 0)
        self.submazes.append(Maze((self.height - row - 1), self.width, self.anchor.add(anchor_offset), self.root))

        return True

    def build(self,
            rng: random.Random,
            gaps: float = DEFAULT_GAPS, gap_factor: float = DEFAULT_GAP_FACTOR,
            vertical: bool = True,
            max_pellets: int = MAX_PELLETS, max_capsules: int = MAX_CAPSULES,
            num_agents: int = DEFAULT_NUM_AGENTS,
            ) -> None:
        """
        Build a full maze into this maze.
        This happens in several parts:
         - Building a "prison" which is the starting places for a team.
         - Building the rest of the maze in the non-prison area.
         - Filling the non-prison area with capture objects (food, capsules).
         - Placing agents on the board prioritizing the left columns.
        """

        self.prison_width = rng.randint(0, MAX_PRISON_WIDTH)

        for prison_col in range(self.prison_width):
            # Compute the actual column the wall for this prison column is on.
            wall_col = (2 * (prison_col + 1)) - 1

            # Mark a full vertical of walls.
            for row in range(self.height):
                self.place_relative(row, wall_col, pacai.core.board.MARKER_WALL)

            # Make an opening at either the top or bottom.
            if (prison_col % 2 == 0):
                self.place_relative(0, wall_col, pacai.core.board.MARKER_EMPTY)
            else:
                self.place_relative(self.height - 1, wall_col, pacai.core.board.MARKER_EMPTY)

        # Everything outside the prison is now a submaze.
        # We will not make a submaze for the prison, since we don't want to edit that.
        anchor_offset = pacai.core.board.Position(0, 2 * self.prison_width)
        non_prison_submaze = Maze(self.height, self.width - (2 * self.prison_width), self.anchor.add(anchor_offset), self.root)
        self.submazes.append(non_prison_submaze)

        # Build the rest of the maze.
        for submaze in self.submazes:
            submaze._build_submaze(rng, gaps = gaps, gap_factor = gap_factor, vertical = vertical)

        # Place agents.
        self._place_agents(rng, num_agents = num_agents)

        # Place capture objects.
        non_prison_submaze._place_capture_markers(rng, max_pellets = max_pellets, max_capsules = max_capsules)

    def _build_submaze(self,
            rng: random.Random,
            gaps: float = DEFAULT_GAPS, gap_factor: float = DEFAULT_GAP_FACTOR,
            vertical: bool = True) -> None:
        """
        Recursively build a maze by making a wall (which will create 0 or two submazes),
        and then building a maze with a different orientation in the submaze.
        """

        # Stop when there is no more room in either orientation.
        if ((self.height <= MIN_MAZE_AXIS_WIDTH) and (self.width <= MIN_MAZE_AXIS_WIDTH)):
            return

        # Decide between vertical and horizontal walls by seeing how much space is left across the primary axis
        # (width if vertical, height if horizontal).
        if (vertical):
            axis_width = self.width
        else:
            axis_width = self.height

        # If there is not enough room on this axis, flip the orientation.
        if (axis_width < (MIN_MAZE_AXIS_WIDTH + 2)):
            vertical = not vertical
            if vertical:
                axis_width = self.width
            else:
                axis_width = self.height

        # Add a wall to the current maze
        wall_slots = range(1, axis_width - 1)

        if (len(wall_slots) == 0):
            return

        wall_index = rng.choice(wall_slots)
        wall_added = self._add_wall(rng, wall_index, gaps = gaps, vertical = vertical)

        # If we did not add a wall, then stop.
        if (not wall_added):
            return

        # Recursively build submazes in the opposite orientation.
        for submaze in self.submazes:
            submaze._build_submaze(rng,
                    gaps = max(1, gaps * gap_factor), gap_factor = gap_factor,
                    vertical = (not vertical))

    def _place_capture_markers(self, rng: random.Random,
            min_pellets: int = MIN_PELLETS, max_pellets: int = MAX_PELLETS,
            min_capsules: int = MIN_CAPSULES, max_capsules: int = MAX_CAPSULES,
            ) -> None:
        """
        Place capture markers/objects on the board.
        This includes pellets and capsules, but not agents.
        """

        # Choose a number of pellets and capsules to place, and randomize the placement order.
        num_pellets = rng.randint(min_pellets, max_pellets)
        num_capsules = rng.randint(min_capsules, max_capsules)

        markers = ([pacai.pacman.board.MARKER_PELLET] * num_pellets) + ([pacai.pacman.board.MARKER_CAPSULE] * num_capsules)
        rng.shuffle(markers)

        # Collect all the empty locations, separated into dead-ends and non-dead-ends.
        dead_ends = []
        non_dead_ends = []

        for row in range(self.height):
            for col in range(self.width):
                if (not self.is_marker_relative(row, col, pacai.core.board.MARKER_EMPTY)):
                    continue

                dead_end = True
                for offset in pacai.core.board.CARDINAL_OFFSETS.values():
                    if (not self.is_marker_relative(row + offset.row, col + offset.col, pacai.core.board.MARKER_EMPTY)):
                        dead_end = False
                        break

                if (dead_end):
                    dead_ends.append((row, col))
                else:
                    non_dead_ends.append((row, col))

        # Shuffle the filling order, making sure that dead-ends get priority.
        rng.shuffle(dead_ends)
        rng.shuffle(non_dead_ends)
        locations = dead_ends + non_dead_ends

        # Keep filling until we run out of objects or locations.
        for marker in markers:
            (row, col) = locations.pop(0)
            self.place_relative(row, col, marker)

            if (len(locations) == 0):
                break

    def _place_agents(self, rng: random.Random, num_agents: int = DEFAULT_NUM_AGENTS) -> None:
        """
        Place agent in this maze.
        Start on the far left column and randomly choose empty locations.
        If there are not enough locations for agents, move to the next column.
        Will raise an error if not all agents can be placed.
        """

        agent_indexes = list(range(num_agents))

        for col in range(self.width):
            empty_rows = [row for row in range(self.height) if self.is_marker_relative(row, col, pacai.core.board.MARKER_EMPTY)]
            rng.shuffle(empty_rows)

            for row in empty_rows:
                marker = pacai.core.board.Marker(str(agent_indexes.pop(0)))
                self.place_relative(row, col, marker)

                if (len(agent_indexes) == 0):
                    return

        raise ValueError("Unable to find enough empty locations to place all agents.")

def generate(
        seed: int | None = None,
        size: int | None = None,
        gaps: float = DEFAULT_GAPS, gap_factor: float | None = None,
        max_pellets: int = MAX_PELLETS, max_capsules: int = MAX_CAPSULES,
        num_agents: int = DEFAULT_NUM_AGENTS,
        ) -> pacai.core.board.Board:
    """
    Generate a random capture board.

    General Procedure:
     - Create a maze for just one team.
       - Create a starting area ("prison") for the team.
       - Recursively create a maze in the rest of the area be making a wall and then making a maze in each new "room" created by the wall.
     - Place agents on the maze, prioritizing the starting area.
     - Place pellets and capsules randomly, ensuring that dead-ends are filled first.
     - Created a mirrored (on both axes) copy of the maze to create the other team's half of the board.
       - Re-index all agents so that evens (and zero) are on the left and odds on the right.

    This process was originally created by Dan Gillick and Jie Tang as a part of
    UC Berkley's CS188 AI project:
    https://ai.berkeley.edu/project_overview.html
    """

    if (seed is None):
        seed = random.randint(0, 2**64)

    rng = random.Random(seed)

    if (size is None):
        size = rng.choice(range(MIN_SIZE, MAX_RANDOM_SIZE + 1, 2))

    if ((size < MIN_SIZE) or (size % 2 != 0)):
        raise ValueError(f"Found disallowed random board size of {size}. Size must be an even number >= {MIN_SIZE}.")

    logging.debug("Generating a Capture board with seed %d and size %d.", seed, size)

    if (gap_factor is None):
        gap_factor = min(MAX_GAP_FACTOR, rng.gauss(DEFAULT_GAP_FACTOR, GAP_FACTOR_STDEV))

    maze = Maze(size, size)
    maze.build(rng, gaps = gaps, gap_factor = gap_factor)
    board = maze.to_board(f"random-{seed}")

    return board

def main() -> int:
    """ Randomly generate a capture board and then print it. """

    parser = argparse.ArgumentParser(description = "Randomly generate a capture board.")
    parser = pacai.core.log.set_cli_args(parser)

    parser.add_argument('--seed', dest = 'seed',
            action = 'store', type = int, default = None,
            help = 'The random seed for this board.')

    parser.add_argument('--size', dest = 'size',
            action = 'store', type = int, default = None,
            help = ('The size for this board.'
                    + f" Must be even and >= {MIN_SIZE}."
                    + f" If not specified, a random number between {MIN_SIZE} and {MAX_RANDOM_SIZE} will be chosen."))

    args = parser.parse_args()
    args = pacai.core.log.init_from_args(parser, args)

    board = generate(args.seed, args.size)
    print(board)

    return 0

if __name__ == '__main__':
    sys.exit(main())
