import abc
import enum
import logging
import random

import pacai.core.action
import pacai.core.agent
import pacai.core.gamestate
import pacai.core.time

class AgentIsolator(abc.ABC):
    """
    An isolator isolates an agent instance from the game being played.
    This "isolation" allows the game to hide or protect state from a agent.
    For example, without isolation an agent can just directly modify the state
    to get all the points and end the game.

    All communication between the game engine and agent should be done via the isolator.
    """

    @abc.abstractmethod
    def init_agents(self, agent_args: list[pacai.core.agent.AgentArguments]) -> None:
        """
        Initialize the agents this isolator will be responsible for.
        """

        pass

    @abc.abstractmethod
    def game_start(self, rng: random.Random, initial_state: pacai.core.gamestate.GameState) -> None:
        """
        Pass along the initial game state to each agent and all them the allotted time to start.
        """

        pass

    @abc.abstractmethod
    def game_complete(self, final_state: pacai.core.gamestate.GameState) -> None:
        """
        Notify all agents that the game is over.
        """

        pass

    @abc.abstractmethod
    def get_action(self, state: pacai.core.gamestate.GameState) -> pacai.core.action.ActionRecord:
        """
        Get the current agent's next action.
        """

        pass

    @abc.abstractmethod
    def close(self) -> None:
        """
        Close the isolator and release all owned resources.
        """

        pass

class Level(enum.Enum):
    NONE = 0
    PROCESS = 1
    TCP = 2

    def get_isolator(self, **kwargs) -> AgentIsolator:
        """ Get an isolator matching the given level. """

        if (self.value == Level.NONE):
            return NoneIsolator(**kwargs)
        if (self.value == Level.PROCESS):
            return ProcessIsolator(**kwargs)
        if (self.value == Level.TCP):
            return TCPIsolator(**kwargs)
        else:
            raise ValueError(f"Unknown isolation level '{self.value}'.")

class NoneIsolator(AgentIsolator):
    """
    An isolator that does not do any isolation between the engine and agents.
    All agents will be run in the same thread (and therefore processes space).
    This is the simplest and fastest of all isolators, but offers the least control and protection.
    Agents cannot be timed out (since they run on the same thread).
    Agents can also access any memory or disk that the core engine has access to.
    """

    def __init__(self, **kwargs) -> None:
        self._agents: list[pacai.core.agent.Agent] | None = None

    def init_agents(self, agent_args: list[pacai.core.agent.AgentArguments]) -> None:
        self._agents = [pacai.core.agent.load(args) for args in agent_args]

    def game_start(self, rng: random.Random, initial_state: pacai.core.gamestate.GameState) -> None:
        if (self._agents is None):
            raise ValueError("Isolator agents has not been initialized.")

        for i in range(len(self._agents)):
            suggested_seed = rng.randint(0, 2**64)
            self._agents[i].game_start(i, suggested_seed, initial_state)

    def game_complete(self, final_state: pacai.core.gamestate.GameState) -> None:
        if (self._agents is None):
            raise ValueError("Isolator agents has not been initialized.")

        for agent in self._agents:
            agent.game_complete(final_state)

    def get_action(self, state: pacai.core.gamestate.GameState) -> pacai.core.action.ActionRecord:
        if (self._agents is None):
            raise ValueError("Isolator agents has not been initialized.")

        if (state.agent_index == -1):
            raise ValueError("Game state does not have an active agent.")

        agent = self._agents[state.agent_index]
        crashed = False

        start_time = pacai.core.time.now()

        try:
            action = agent.get_action(state)
        except Exception as ex:
            logging.warning("Agent '%s' (%d) crashed.", agent.name, state.agent_index, exc_info = ex)

            crashed = True
            action = pacai.core.action.STOP

        end_time = pacai.core.time.now()

        return pacai.core.action.ActionRecord(
                agent_index = state.agent_index,
                action = action,
                duration = end_time.sub(start_time),
                crashed = crashed)


    def close(self) -> None:
        self._agents = None

# TEST
class ProcessIsolator(AgentIsolator):
    pass

# TEST
class TCPIsolator(AgentIsolator):
    pass
