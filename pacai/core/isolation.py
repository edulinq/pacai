import abc
import enum
import logging
import random

import pacai.core.action
import pacai.core.agent
import pacai.core.agentinfo
import pacai.core.gamestate
import pacai.util.time

class AgentIsolator(abc.ABC):
    """
    An isolator isolates an agent instance from the game being played.
    This "isolation" allows the game to hide or protect state from a agent.
    For example, without isolation an agent can just directly modify the state
    to get all the points and end the game.

    All communication between the game engine and agent should be done via the isolator.
    """

    @abc.abstractmethod
    def init_agents(self, agent_infoss: dict[int, pacai.core.agentinfo.AgentInfo]) -> None:
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
    def get_action(self, state: pacai.core.gamestate.GameState, user_inputs: list[pacai.core.action.Action]) -> pacai.core.action.ActionRecord:
        """
        Get the current agent's next action.
        User inputs may be provided by the UI if available.
        """

        pass

    @abc.abstractmethod
    def close(self) -> None:
        """
        Close the isolator and release all owned resources.
        """

        pass

class Level(enum.Enum):
    NONE = 'none'
    PROCESS = 'process'
    TCP = 'tcp'

    def get_isolator(self, **kwargs) -> AgentIsolator:
        """ Get an isolator matching the given level. """

        if (self == Level.NONE):
            return NoneIsolator(**kwargs)
        elif (self == Level.PROCESS):
            return ProcessIsolator(**kwargs)
        elif (self == Level.TCP):
            return TCPIsolator(**kwargs)
        else:
            raise ValueError(f"Unknown isolation level '{self}'.")

LEVELS: list[str] = [item.value for item in Level]

class NoneIsolator(AgentIsolator):
    """
    An isolator that does not do any isolation between the engine and agents.
    All agents will be run in the same thread (and therefore processes space).
    This is the simplest and fastest of all isolators, but offers the least control and protection.
    Agents cannot be timed out (since they run on the same thread).
    Agents can also access any memory or disk that the core engine has access to.
    """

    def __init__(self, **kwargs) -> None:
        self._agents: dict[int, pacai.core.agent.Agent] = {}

    def init_agents(self, all_agent_infoss: dict[int, pacai.core.agentinfo.AgentInfo]) -> None:
        self._agents = {}
        for (agent_index, agent_info) in all_agent_infoss.items():
            self._agents[agent_index] = pacai.core.agent.load(agent_info)

    def game_start(self, rng: random.Random, initial_state: pacai.core.gamestate.GameState) -> None:
        for (agent_index, agent) in self._agents.items():
            suggested_seed = rng.randint(0, 2**64)
            agent.game_start(agent_index, suggested_seed, initial_state)

    def game_complete(self, final_state: pacai.core.gamestate.GameState) -> None:
        for agent in self._agents.values():
            agent.game_complete(final_state)

    def get_action(self, state: pacai.core.gamestate.GameState, user_inputs: list[pacai.core.action.Action]) -> pacai.core.action.ActionRecord:
        if (state.agent_index == -1):
            raise ValueError("Game state does not have an active agent.")

        agent = self._agents[state.agent_index]
        crashed = False

        start_time = pacai.util.time.now()

        try:
            action = agent.get_action(state, user_inputs)
        except Exception as ex:
            logging.warning("Agent '%s' (%d) crashed.", agent.name, state.agent_index, exc_info = ex)

            crashed = True
            action = pacai.core.action.STOP

        end_time = pacai.util.time.now()

        return pacai.core.action.ActionRecord(
                agent_index = state.agent_index,
                action = action,
                duration = end_time.sub(start_time),
                crashed = crashed)


    def close(self) -> None:
        self._agents.clear()

# TEST
# class ProcessIsolator(AgentIsolator):
class ProcessIsolator(NoneIsolator):
    pass

# TEST
# class TCPIsolator(AgentIsolator):
class TCPIsolator(NoneIsolator):
    pass
