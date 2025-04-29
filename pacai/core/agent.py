import abc
import random
import typing

import pacai.core.action
import pacai.core.agentinfo
import pacai.core.gamestate
import pacai.util.reflection

class Agent(abc.ABC):
    """ The base for all agents in the pacai system. """

    def __init__(self, agent_args: pacai.core.agentinfo.AgentInfo, *args, **kwargs) -> None:
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

        self._rng: random.Random = random.Random()
        """
        The RNG this agent should use whenever it wants randomness.
        This object will be constructed right away,
        but will be recreated with the suggested seed from the game engine during game_start().
        """

    @abc.abstractmethod
    def get_action(self, state: pacai.core.gamestate.GameState, user_inputs: list[pacai.core.action.Action]) -> pacai.core.action.Action:
        """
        Get an action for this agent given the current state of the game.
        Agents may keep internal state, but the given state should be considered the source of truth.
        Calls to this method may be subject to a timeout.
        """

        pass

    def game_start(self, agent_index: int, suggested_seed: int, initial_state: pacai.core.gamestate.GameState) -> None:
        """
        Notify this agent that the game is about to start.
        The provided agent index is the game's index/id for this agent.
        The state represents the initial state of the game.
        Any precomputation for this game should be done in this method.
        Calls to this method may be subject to a timeout.
        """

        self._rng = random.Random(suggested_seed)

    def game_complete(self, final_state: pacai.core.gamestate.GameState) -> None:
        """
        Notify this agent that the game has concluded.
        Agents should use this as an opportunity to make any final calculations and close any game-related resources.
        """

        pass

@typing.runtime_checkable
class EvaluationFunction(typing.Protocol):
    """
    A function that an agent can use to score a game state.
    """

    def __call__(self, state: pacai.core.gamestate.GameState) -> float:
        """
        Compute a score for a state that an agent can use to decide actions.
        """

        pass

def base_eval(state: pacai.core.gamestate.GameState) -> float:
    """ The most basic evaluation function, which just uses the state's current score. """

    return float(state.score)

def load(agent_args: pacai.core.agentinfo.AgentInfo) -> Agent:
    agent = pacai.util.reflection.new_object(agent_args.name, agent_args)

    if (not isinstance(agent, Agent)):
        raise ValueError(f"Loaded class is not an agent: '{agent_args.name}'.")

    return agent
