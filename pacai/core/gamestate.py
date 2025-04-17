import abc

import pacai.core.action
import pacai.core.board

# TEST - Mutability semantics?
#      - How will this tie in with isolation level? Will the level be responsible for copies?

# TODO - Do we need to track a "winner" or winning agent?

class GameState(abc.ABC):
    """
    The base for all game states in pacai.
    A game state should contain all the information about the current state of the game.

    Game states should only be interacted with via their methods and not their member variables
    (since this class has been optimized for performance).
    """

    def __init__(self,
            board: pacai.core.board.Board | None = None,
            agent_index: int = -1,
            game_over: bool = False,
            timeout: bool = False,
            **kwargs) -> None:
        if (board is None):
            raise ValueError("Cannot construct a game state without a board.")

        self.board: pacai.core.board.Board = board
        """ The current board. """

        self.agent_index: int = agent_index
        """
        The index of the agent with the current move.
        -1 indicates that the agent to move has not been selected yet.
        """

        self.game_over: bool = game_over
        """ Indicates that this state represents a complete game. """

        self.timeout: bool = timeout
        """ Indicates that the game ended in a timeout. """

        self.last_agent_actions: dict[int, pacai.core.action.Action] = {}
        """ Keep track of the last action that each agent made. """

    def get_agent_position(self) -> pacai.core.board.Position | None:
        """ Get the position of the current active agent. """

        if (self.agent_index < 0):
            raise ValueError("No agent is active, cannot get position.")

        return self.board.get_agent_position(self.agent_index)

    @abc.abstractmethod
    def get_legal_actions(self) -> list[pacai.core.action.Action]:
        """ Get the moves that the current agent is allowed to make. """

        pass
