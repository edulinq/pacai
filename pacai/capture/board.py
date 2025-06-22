import argparse
import logging
import random
import sys

import pacai.core.board
import pacai.core.log
import pacai.pacman.board

# TODO - Needs more updates.

# TEST - Old size is always 16x16
# DEFAULT_SIZE: int = 16

# TEST
MIN_SIZE: int = 10

MAX_RANDOM_SIZE: int = 32
""" The maximum size for a maze with unspecified size. """

def generate(seed: int | None = None, size: int | None = None) -> pacai.core.board.Board:
    """
    Generare a radom capture board.

    TEST

    Algorithm:
     - Start with an empty grid.
     - Draw a wall with gaps, dividing the grid in 2.
     - Repeat recursively for each sub-grid.

    Pacman Details:
     - Players 1 and 3 always start in the bottom left; 2 and 4 in the top right.
     - Food is placed in dead ends and then randomly
        (though not too close to the pacmen starting positions).

    Notes:
     - The final map includes a symmetric, flipped copy.
     - The first wall has k gaps, the next wall has k / 2 gaps, etc. (min=1).

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
        raise ValueError(f"Found dissallowed random board size of {size}. Size must be an even number >= {MIN_SIZE}.")

    logging.debug("Generating a Capture board with seed %d and size %d.", seed, size)

    # TEST - Prison location?
    _add_walls(rng, board)

    base_maze = _generate_maze(rng)

    ''' TEST
    maze.to_map()
    add_pacman_stuff(rng, maze, 2 * (maze.height * int(maze.width / 20)), 4, skip)
    '''

    # TEST - Double and add two for a border?
    board = pacai.core.board.create_empty(source = f"random-{seed}", height = size, width = size)

    # TEST
    print('---')
    print(board)
    print('---')

    # TEST

    # TEST
    return board

def _generate_maze(rng: random.Random, size: int) -> Maze:
    # TEST
    size = 16

    maze = Maze(size, size)

    # TEST
    gap_factor = min(0.65, rng.gauss(0.5, 0.1))

    # TEST - integrate skip into Maze class.
    skip = make_with_prison(rng, maze, depth = 0, gaps = 3, vert = True, min_width = 1, gap_factor = gap_factor)

    return maze


# TEST
MAX_DIFFERENT_MAZES = 10000

# TEST
class Maze:
    """
    A recursive definition of a maze.

    Each maze has an "anchor", which is the position of its top-left (northwest) corner in it's parent.
    There is only one collection of markers that backs all mazes in a tree.
    """

    def __init__(self,
            height: int, width: int,
            anchor: pacai.core.board.Position | None = None, root: typing.Union['Maze', None] = None,
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

        self.rooms: list['Maze'] = []
        """ The submazes ("rooms"/children) in this maze. """

    def place_relative(self, row: int, col: int, marker: pacai.core.board.Marker) -> None:
        """ Place a marker in the grid according to the relative coordinates of this submaze. """

        grid[self.anchor.row + row][self.anchor.col + col] = marker

    def is_marker_relative(self, row: int, col: int, marker: pacai.core.board.Marker) -> None:
        """ Check if the given marker exists at the relative coordinates of this submaze. """

        true_row = self.anchor.row + row
        true_col = self.anchor.col + col

        # No markers are out-of-bounds.
        if ((true_row < 0) or (true_row >= len(self.grid)) or (true_col < 0) or (true_col >= len(self.grid[0]))):
            return False

        return (grid[true_row][true_col] == marker)

    # TEST - to_board() ?
    def to_map(self):
        """
        Add a flipped symmetric copy on the right.
        Add a border.
        """

        # Add a flipped symmetric copy
        for row in range(self.height):
            for col in range(self.width - 1, -1, -1):
                self.grid[self.height - row - 1].append(self.grid[row][col])
        self.width *= 2

        # Add a border
        for row in range(self.height):
            self.grid[row] = [pacai.core.board.MARKER_WALL] + self.grid[row] + [pacai.core.board.MARKER_WALL]
        self.width += 2

        self.grid.insert(0, [pacai.core.board.MARKER_WALL for _ in range(self.width)])
        self.grid.append([pacai.core.board.MARKER_WALL for _ in range(self.width)])
        self.height += 2

    def add_wall(self, rng: random.Random, col: int, gaps: float = 1.0, vertical = True) -> bool:
        """
        Try to add a vertical wall with gaps at the given location.
        Return True if a wall was added, False otherwise.
        """

        if (vertical):
            return self._add_vertical_wall(rng, index, gaps = gaps)

        return self._add_horizontal_wall(rng, index, gaps = gaps)

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

        # By placing a wall, we have created two new rooms (on each side of the wall).

        # One room to the left.
        self.rooms.append(Maze(self.height, col, anchor = self.anchor, root = self.root))

        # One room to the right.
        anchor_offset = pacai.core.board.Position(0, col + 1)
        self.rooms.append(Maze(self.height, (self.width - col - 1), self.anchor.add(anchor_offset), self.root))

        return True

    def _add_horizontal_wall(self, rng: random.Random, row: int, gaps: int = 1) -> bool:
        """
        Try to add a horizontal wall with gaps at the given row.
        Return True if a wall was added, False otherwise.
        """

        # Choose the specific number of gaps we are expecting.
        gaps = int(round(min(self.width, gaps)))

        # The places (cols) that we may put a wall.
        slots = list(range(self.width))

        # If there are empty spaces directly to the left/right of our proposed wall,
        # then don't put a wall marker directly in front of those respective spaces.
        # This prevents us blocking entrances into our submaze.

        if (self.is_marker_relative(row, -1, pacai.core.board.MARKER_EMPTY)):
            slots.remove(0)

        if (self.is_marker_relative(row, self.width, pacai.core.board.MARKER_EMPTY)):
            slots.remove(self.width - 1)

        # If we cannot provided the requested number of gaps, then don't put down the wall.
        if (len(slots) <= gaps):
            return False

        # Randomize where we will put our walls.
        rng.shuffle(slots)

        # Skip the first slots (these are gaps), and place the rest.
        for col in slots[gaps:]:
            self.place_relative(row, col, pacai.core.board.MARKER_WALL)

        # By placing a wall, we have created two new rooms (on each side of the wall).

        # One room above.
        self.rooms.append(Maze(row, self.width, anchor = self.anchor, root = self.root))

        # One room below.
        anchor_offset = pacai.core.board.Position(row + 1, 0)
        self.rooms.append(Maze((self.height - row - 1), self.width, self.anchor.add(anchor_offset), self.root))

        return True






# TEST




def make_with_prison(rng, room, depth, gaps=1, vert=True, min_width=1, gap_factor=0.5):
    """
    Build a maze with 0,1,2 layers of prison (randomly).
    """

    p = rng.randint(0, 2)
    proll = rng.random()
    if proll < 0.5:
        p = 1
    elif proll < 0.7:
        p = 0
    elif proll < 0.9:
        p = 2
    else:
        p = 3

    add_r, add_c = room.anchor
    for j in range(p):
        cur_col = 2 * (j + 1) - 1
        for row in range(room.height):
            room.root.grid[row][cur_col] = pacai.core.board.MARKER_WALL

        if j % 2 == 0:
            room.root.grid[0][cur_col] = pacai.core.board.MARKER_EMPTY
        else:
            room.root.grid[room.height - 1][cur_col] = pacai.core.board.MARKER_EMPTY

    room.rooms.append(Maze(room.height, room.width - (2 * p), (add_r, add_c + (2 * p)), room.root))
    for sub_room in room.rooms:
        make(rng, sub_room, depth + 1, gaps, vert, min_width, gap_factor)

    return 2 * p

def make(rng, room, depth, gaps=1, vert=True, min_width=1, gap_factor=0.5):
    """
    Recursively build a maze.
    """

    # Extreme base case
    if room.height <= min_width and room.width <= min_width:
        return

    # Decide between vertical and horizontal wall
    if vert:
        num = room.width
    else:
        num = room.height

    if num < min_width + 2:
        vert = not vert
        if vert:
            num = room.width
        else:
            num = room.height

    # Add a wall to the current room
    if depth == 0:
        wall_slots = [num - 2]  # Fix the first wall
    else:
        wall_slots = range(1, num - 1)

    if len(wall_slots) == 0:
        return

    choice = rng.choice(wall_slots)
    if not room.add_wall(rng, choice, gaps, vertical = vert):
        return

    # Recursively add walls
    for sub_room in room.rooms:
        make(rng, sub_room, depth + 1, max(1, gaps * gap_factor), not vert, min_width, gap_factor)

def copy_grid(grid):
    new_grid = []

    for row in range(len(grid)):
        new_grid.append([])
        for col in range(len(grid[row])):
            new_grid[row].append(grid[row][col])

    return new_grid

def add_pacman_stuff(rng, maze, max_food=60, max_capsules=4, toskip=0):
    """
    Add pacmen starting position.
    Add food at dead ends plus some extra.
    """

    # Parameters
    max_depth = 2

    # Add food at dead ends
    depth = 0
    total_food = 0

    while True:
        new_grid = copy_grid(maze.grid)
        depth += 1
        num_added = 0

        for row in range(1, maze.height - 1):
            for col in range(1 + toskip, int(maze.width / 2) - 1):
                if (row > maze.height - 6) and (col < 6):
                    continue

                if maze.grid[row][col] != pacai.core.board.MARKER_EMPTY:
                    continue

                neighbors = 0
                neighbors += (maze.grid[row - 1][col] == pacai.core.board.MARKER_EMPTY)
                neighbors += (maze.grid[row][col - 1] == pacai.core.board.MARKER_EMPTY)
                neighbors += (maze.grid[row + 1][col] == pacai.core.board.MARKER_EMPTY)
                neighbors += (maze.grid[row][col + 1] == pacai.core.board.MARKER_EMPTY)

                if neighbors == 1:
                    new_grid[row][col] = pacai.pacman.board.MARKER_PELLET
                    new_grid[maze.height - row - 1][maze.width - col - 1] = pacai.pacman.board.MARKER_PELLET
                    num_added += 2
                    total_food += 2

        maze.grid = new_grid
        if num_added == 0:
            break

        if depth >= max_depth:
            break

    # Starting pacmen positions
    maze.grid[maze.height - 2][1] = '3'
    maze.grid[maze.height - 3][1] = '1'
    maze.grid[1][maze.width - 2] = '4'
    maze.grid[2][maze.width - 2] = '2'

    # Add capsules
    total_capsules = 0
    while (total_capsules < max_capsules):
        row = rng.randint(1, maze.height - 1)
        col = rng.randint(1 + toskip, int(maze.width / 2) - 2)

        if (row > maze.height - 6) and (col < 6):
            continue

        if (abs(col - int(maze.width / 2)) < 3):
            continue

        if maze.grid[row][col] == pacai.core.board.MARKER_EMPTY:
            maze.grid[row][col] = pacai.pacman.board.MARKER_CAPSULE
            maze.grid[maze.height - row - 1][maze.width - col - 1] = pacai.pacman.board.MARKER_CAPSULE
            total_capsules += 2

    # Extra random food
    while (total_food < max_food):
        row = rng.randint(1, maze.height - 1)
        col = rng.randint(1 + toskip, int(maze.width / 2) - 1)

        if (row > maze.height - 6) and (col < 6):
            continue

        if (abs(col - int(maze.width / 2)) < 3):
            continue

        if maze.grid[row][col] == pacai.core.board.MARKER_EMPTY:
            maze.grid[row][col] = pacai.pacman.board.MARKER_PELLET
            maze.grid[maze.height - row - 1][maze.width - col - 1] = pacai.pacman.board.MARKER_PELLET
            total_food += 2

def main() -> int:
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
    args = pacai.core.log.init_from_args(args)

    board = generate(args.seed, args.size)
    print(board)

    return 0

if __name__ == '__main__':
    sys.exit(main())
