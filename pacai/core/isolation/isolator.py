import abc
import random

import pacai.core.action
import pacai.core.agentaction
import pacai.core.agentinfo
import pacai.core.gamestate

class AgentIsolator(abc.ABC):
    """
    An isolator isolates an agent instance from the game being played.
    This "isolation" allows the game to hide or protect state from a agent.
    For example, without isolation an agent can just directly modify the state
    to get all the points and end the game.

    All communication between the game engine and agent should be done via the isolator.
    """

    @abc.abstractmethod
    def init_agents(self, agent_infos: dict[int, pacai.core.agentinfo.AgentInfo]) -> None:
        """
        Initialize the agents this isolator will be responsible for.
        """

    @abc.abstractmethod
    def game_start(self,
            rng: random.Random,
            initial_state: pacai.core.gamestate.GameState,
            timeout: float,
            ) -> dict[int, pacai.core.agentaction.AgentActionRecord]:
        """
        Pass along the initial game state to each agent and all them the allotted time to start.
        """

    @abc.abstractmethod
    def game_complete(self,
            final_state: pacai.core.gamestate.GameState,
            timeout: float,
            ) -> dict[int, pacai.core.agentaction.AgentActionRecord]:
        """
        Notify all agents that the game is over.
        """

    @abc.abstractmethod
    def get_action(self,
            state: pacai.core.gamestate.GameState,
            user_inputs: list[pacai.core.action.Action],
            timeout: float,
            ) -> pacai.core.agentaction.AgentActionRecord:
        """
        Get the current agent's next action.
        User inputs may be provided by the UI if available.
        """

    @abc.abstractmethod
    def close(self) -> None:
        """
        Close the isolator and release all owned resources.
        This call should not communicate with agents and forcibly release any agent resources.
        """
