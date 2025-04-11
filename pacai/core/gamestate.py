import abc

import pacai.core.board

class GameState(abc.ABC):
    """
    The base for all game states in pacai.
    A game state should contain all the information about the current state of the game.

    Game states should only be interacted with via their methods and not their member variables
    (since this class has been optimized for performance).
    """

    def __init__(self, board: pacai.core.board.Board) -> None:
        self._board: pacai.core.board.Board = board
