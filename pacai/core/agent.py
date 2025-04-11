import abc
import typing

import pacai.core.action
import pacai.core.gamestate

DEFAULT_MOVE_DELAY: int = 100
""" The defaut delay between agent moves. """

class Agent(abc.ABC):
    """ The base for all agents in the pacai system. """

    def __init__(self, name: str, move_delay: int = DEFAULT_MOVE_DELAY) -> None:
        self.name: str = name
        """ The name of this agent. """

        self.move_delay: int = move_delay
        """
        The delay between moves for this agent.
        This value is abstract and has not real units,
        i.e., it is not something like a number of seconds.
        Instead, this is a relative "time" that is used to decide the next agent to move.
        Lower values (relative to other agents) times means the agent will move more times and thus be "faster".
        For example, an agent with a move delay of 50 will move twice as often as an agent with a move delay of 100.
        """

    # TEST
    def get_action(self, state: pacai.core.gamestate.GameState) -> pacai.core.action.Action:
        pass

    # TEST
    def game_start(self, agent_index: int, game_state: pacai.core.gamestate.GameState) -> None:
        pass

    # TEST
    def game_complete(self, game_state: pacai.core.gamestate.GameState) -> None:
        pass

class Ticket(typing.NamedTuple):
    """
    An agent's Ticket determines when they will move next.
    A ticket is a tuple of three values: (next move time, last move time, number of moves).
    The agent with the lowest ticket (starting with the first value and moving to the next on a tie) gets to move next.
    All "time" values represented by a ticket are abstract and do not relate to any actual time units.
    """

    next_time: int
    """ The next time the ticket is allowed to move. """

    last_time: int
    """ The last time that the agent moved. """

    num_moves: int
    """ The total number of times this agent has moved so far. """
