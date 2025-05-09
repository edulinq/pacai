"""
This file provides to the logic to work with 8 Puzzle problems.
8 Puzzle is a smaller variant of the [15 Puzzle game](https://en.wikipedia.org/wiki/15_puzzle).
"""

import random

import pacai.core.action
import pacai.core.board

DIM: int = 3
""" The length of one dimension/size of the puzzle. """

LENGTH: int = DIM * DIM
""" The total number of numbers in the puzzle. """

SOLVED_NUMBERS: list[int] = list(range(LENGTH))
""" The sequence of numbers that represents a solved puzzle. """

BLANK_NUMBER: int = 0
""" The number used to represent the blank space. """

class EightPuzzleBoard:
    """
    An instance of an 8 Puzzle board.

    8 Puzzle (a smaller variant of 15 Puzzle) is a type of sliding puzzle
    where the numbers 1-8 are arranged on square tiles on a square grid with one blank space
    (sometimes represented with a 0).
    The goal of the puzzle is to slide the tiles so that the empty space
    is in the top left and all other tiles are in increasing order.
    A solved puzzles looks like:
    ```
        -------------
        |   | 1 | 2 |
        -------------
        | 3 | 4 | 5 |
        -------------
        | 6 | 7 | 8 |
        -------------
    ```

    An interesting note about 8 Puzzle is that every configuration of the board is both
    a valid puzzle and a valid starting location
    (image a game of chess where any configuration of the board is a valid starting position).

    In the real world, you move tiles into the blank space on the puzzle.
    In this representation, we will instead "slide" the blank space in one of the four cardinal directions.
    This makes our representation of moves easier, since we don't have to keep track of which tile is being moved
    (it is always the blank tile/space).
    """

    def __init__(self, numbers: list[int]) -> None:
        if (len(numbers) != LENGTH):
            raise ValueError(f"Incorrect number of puzzle inputs. Required: {LENGTH}, Found: {len(numbers)}.")

        for (i, value) in enumerate(numbers):
            if ((value < 0) or (value >= LENGTH)):
                raise ValueError(f"Puzzle value at index {i} is out of bounds. Found {value}, must be in [0, {LENGTH - 1}].")

        self._numbers = numbers.copy()

    def is_solved(self) -> bool:
        """ Check if this puzzle in in the solved position. """

        return (self._numbers == SOLVED_NUMBERS)

    def get_legal_actions(self) -> list[pacai.core.action.Action]:
        """
        Get a list if the current legal actions.

        Legal actions consists of cardinal directions that the blank tile can be moved to.

        Note that these moves are the opposite of the real world where you slide another tile into the blank tile's space.
        """

        actions = []

        blank_position = self.get_blank_position()

        for (action, offset) in pacai.core.board.CARDINAL_OFFSETS.items():
            new_position = blank_position.add(offset)
            if ((new_position.row < 0) or (new_position.row >= DIM) or (new_position.col < 0) or (new_position.col >= DIM)):
                continue

            actions.append(action)

        return actions

    def get_blank_position(self) -> pacai.core.board.Position:
        """ Get the position of the blank space. """

        index = self._numbers.index(BLANK_NUMBER)
        row = index // DIM
        col = index % DIM

        return pacai.core.board.Position(row, col)

    def apply_action(self, action: pacai.core.action.Action) -> 'EightPuzzleBoard':
        """ Returns a new EightPuzzleBoard after taking the given action. """

        offset = pacai.core.board.CARDINAL_OFFSETS.get(action, None)
        if (offset is None):
            raise ValueError(f"Illegal action: '{action}'.")

        # Get the old and new positions.
        old_blank_position = self.get_blank_position()
        new_blank_position = old_blank_position.add(offset)

        # Convert the positions to indexes.
        old_blank_index = (old_blank_position.row * DIM) + old_blank_position.col
        new_blank_index = (new_blank_position.row * DIM) + new_blank_position.col

        # Get a copy of the numbers, and swap the old/new blank positions.
        new_numbers = self._numbers.copy()
        new_numbers[old_blank_index], new_numbers[new_blank_index] = new_numbers[new_blank_index], new_numbers[old_blank_index]

        return EightPuzzleBoard(new_numbers)

    def __eq__(self, other: object) -> bool:
        if (not isinstance(other, EightPuzzleBoard)):
            return False

        return self._numbers == other._numbers

    def __hash__(self) -> int:
        return hash(str(self._numbers))

    def __lt__(self, other: object) -> bool:
        if (not isinstance(other, EightPuzzleBoard)):
            raise TypeError(f"Puzzles must be of the same type, found '{type(self)}' and '{type(other)}'.")

        return self._numbers < other._numbers

    def __str__(self) -> str:
        separator = '-' * (DIM * (DIM + 1) + 1)
        lines = [separator]

        for row in range(DIM):
            line = '|'

            for col in range(DIM):
                index = (row * DIM) + col

                value: str | int = self._numbers[index]
                if (value == BLANK_NUMBER):
                    value = ' '

                line += f" {value} |"

            lines.append(line)
            lines.append(separator)

        return "\n".join(lines)

    def __repr__(self) -> str:
        return str(self._numbers)

def from_rng(rng: random.Random, move_count: int = 100) -> EightPuzzleBoard:
    """
    Create a new EightPuzzleBoard from a random seed.
    The given number of random moves will be taken to scramble the board
    (starting from the solved board).
    """

    puzzle = EightPuzzleBoard(SOLVED_NUMBERS)
    for _ in range(move_count):
        actions = puzzle.get_legal_actions()
        action = rng.sample(actions, 1)[0]
        puzzle = puzzle.apply_action(action)

    return puzzle
