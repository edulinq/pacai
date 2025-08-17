"""
This file provides to the logic to work with 8 Puzzle problems.
8 Puzzle is a smaller variant of the [15 Puzzle game](https://en.wikipedia.org/wiki/15_puzzle).
"""

import pacai.core.search
import pacai.eightpuzzle.board

class EightPuzzleNode(pacai.core.search.SearchNode):
    """
    The search node for an 8 Puzzle problem,
    which is just the puzzle's board.
    """

    def __init__(self, board: pacai.eightpuzzle.board.EightPuzzleBoard) -> None:
        self.board = board

    def __eq__(self, other: object) -> bool:
        if (not isinstance(other, EightPuzzleNode)):
            return False

        return self.board == other.board

    def __hash__(self) -> int:
        return hash(self.board)

    def __lt__(self, other: object) -> bool:
        if (not isinstance(other, EightPuzzleNode)):
            raise TypeError(f"Puzzles must be of the same type, found '{type(self)}' and '{type(other)}'.")

        return self.board < other.board

class EightPuzzleSearchProblem(pacai.core.search.SearchProblem):
    """
    A search problem for finding an 8 Puzzle solution.
    """

    def __init__(self, board: pacai.eightpuzzle.board.EightPuzzleBoard):
        super().__init__()

        self.board = board
        """ The starting board for this problem. """

    def get_starting_node(self) -> EightPuzzleNode:
        return EightPuzzleNode(self.board)

    def is_goal_node(self, node: EightPuzzleNode) -> bool:
        return node.board.is_solved()

    def get_successor_nodes(self, node: EightPuzzleNode) -> list[pacai.core.search.SuccessorInfo]:
        successors = []
        for action in node.board.get_legal_actions():
            new_board = node.board.apply_action(action)
            successors.append(pacai.core.search.SuccessorInfo(EightPuzzleNode(new_board), action, 1))

        return successors
