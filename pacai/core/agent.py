import abc
import typing

import pacai.core.action
import pacai.core.gamestate
import pacai.util.reflection

DEFAULT_MOVE_DELAY: int = 100
""" The default delay between agent moves. """

class AgentArguments:
    def __init__(self, name: str = '',
            move_delay: int = DEFAULT_MOVE_DELAY,
            **kwargs) -> None:
        name = name.strip()
        if (len(name) == 0):
            raise ValueError("Agent name cannot be empty.")

        if (move_delay <= 0):
            raise ValueError("Agent move delay must be > 0.")

        self.name: str = name
        self.move_delay: int = move_delay

        self.other_arguments: dict[str, typing.Any] = kwargs

class Agent(abc.ABC):
    """ The base for all agents in the pacai system. """

    def __init__(self, agent_args: AgentArguments, *args, **kwargs) -> None:
        self.name: str = agent_args.name
        """ The name of this agent. """

        self.move_delay: int = agent_args.move_delay
        """
        The delay between moves for this agent.
        This value is abstract and has not real units,
        i.e., it is not something like a number of seconds.
        Instead, this is a relative "time" that is used to decide the next agent to move.
        Lower values (relative to other agents) times means the agent will move more times and thus be "faster".
        For example, an agent with a move delay of 50 will move twice as often as an agent with a move delay of 100.
        """

    @abc.abstractmethod
    def get_action(self, state: pacai.core.gamestate.GameState, user_inputs: list[pacai.core.action.Action]) -> pacai.core.action.Action:
        """
        Get an action for this agent given the current state of the game.
        Agents may keep internal state, but the given state should be considered the source of truth.
        Calls to this method may be subject to a timeout.
        """

        pass

    @abc.abstractmethod
    def game_start(self, agent_index: int, suggested_seed: int, initial_state: pacai.core.gamestate.GameState) -> None:
        """
        Notify this agent that the game is about to start.
        The provided agent index is the game's index/id for this agent.
        The state represents the initial state of the game.
        Any precomputation for this game should be done in this method.
        Calls to this method may be subject to a timeout.
        """

        pass

    @abc.abstractmethod
    def game_complete(self, final_state: pacai.core.gamestate.GameState) -> None:
        """
        Notify this agent that the game has concluded.
        Agents should use this as an opportunity to make any final calculations and close any game-related resources.
        """

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

    def next(self, move_delay: int) -> 'Ticket':
        """ Get the next ticket in the sequence for this agent. """

        return Ticket(
            next_time = self.next_time + move_delay,
            last_time = self.next_time,
            num_moves = self.num_moves + 1,
        )

def load(agent_args: AgentArguments) -> Agent:
    agent = pacai.util.reflection.new_object(agent_args.name, agent_args)

    if (not isinstance(agent, Agent)):
        raise ValueError(f"Loaded class is not an agent: '{agent_args.name}'.")

    return agent
