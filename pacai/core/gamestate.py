import abc

import pacai.core.action
import pacai.core.board

class GameState(abc.ABC):
    """
    The base for all game states in pacai.
    A game state should contain all the information about the current state of the game.

    Game states should only be interacted with via their methods and not their member variables
    (since this class has been optimized for performance).
    """

    def __init__(self,
            board: pacai.core.board.Board,
            agent_index: int = -1,
            game_over: bool = False,
            timeout: bool = False) -> None:
        self.agent_index: int = agent_index
        """
        The index of the agent with the current move.
        -1 indicates that the agent to move has not been selected yet.
        """

        self.board: pacai.core.board.Board = board
        """ The current board. """

        self.game_over: bool = game_over
        """ Indicates that this state represents a complete game. """

        self.timeout: bool = timeout
        """ Indicates that the game ended in a timeout. """

    @abc.abstractmethod
    def get_legal_actions(self) -> list[pacai.core.action.Action]:
        """ Get the moves that the current agent is allowed to make. """

        pass
