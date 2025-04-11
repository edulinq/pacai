import abc
import enum

import pacai.core.action
import pacai.core.agent
import pacai.core.gamestate

class Isolator(abc.ABC):
    """
    An isolator isolates an agent instance from the game being played.
    This "isolation" allows the game to hide or protect state from a agent.
    For example, without isolation an agent can just directly modify the state
    to get all the points and end the game.

    All communication between the game engine and agent should be done via the isolator.
    """

    @abc.abstractmethod
    def game_init(self, agents: list[pacai.core.agent.Agent]) -> None:
        """
        Initialize the isolator with the given agents.
        Called when a game is just preparing to start.
        """

        pass

    @abc.abstractmethod
    def game_start(self, initial_state: pacai.core.gamestate.GameState) -> None:
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
    def get_action(self, agent_index: int, state: pacai.core.gamestate.GameState) -> pacai.core.action.Action:
        """
        Get an agent's next action.
        """

        pass

class Level(enum.Enum):
    NONE = 0
    PROCESS = 1
    TCP = 2

    def get_isolator(self) -> Isolator:
        """ Get an isolator matching the given level. """

        if (self.value == Level.NONE):
            return NoneIsolator()
        if (self.value == Level.PROCESS):
            return ProcessIsolator()
        if (self.value == Level.TCP):
            return TCPIsolator()
        else:
            raise ValueError(f"Unknown isolation level '{self.value}'.")

# TEST
class NoneIsolator(abc.ABC):
    pass

# TEST
class ProcessIsolator(abc.ABC):
    pass

# TEST
class TCPIsolator(abc.ABC):
    pass
