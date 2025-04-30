import abc
import copy

import pacai.core.action
import pacai.core.agentinfo
import pacai.core.board
import pacai.core.ticket

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
            score: int = 0,
            turn_count: int = 0,
            agent_infos: dict[int, pacai.core.agentinfo.AgentInfo] = {},
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

        self.last_actions: dict[int, pacai.core.action.Action] = {}
        """ Keep track of the last action that each agent made. """

        self.score: int = score
        """ The current score of the game. """

        self.turn_count: int = turn_count
        """ The number of turns (agent actions) that the game has had. """

        self.move_delays: dict[int, int] = {}
        """
        The current move delay for each agent.
        Every agent should always have a move delay.
        """

        self.tickets: dict[int, pacai.core.ticket.Ticket] = {}
        """
        The current ticket for each agent.
        Every agent should always have a ticket once the game starts (even if it is not taking a move).
        """

        # Initialize data from agent arguments.
        for (agent_index, agent_info) in agent_infos.items():
            self.move_delays[agent_index] = agent_info.move_delay

    def game_start(self):
        """
        Indicate that the game is starting.
        This will initialize some state like tickets.
        """

        # Issue initial tickets.
        for (agent_index, move_delay) in self.move_delays.items():
            self.tickets[agent_index] = pacai.core.ticket.Ticket(agent_index + move_delay, 0, 0)

        # Choose the first agent to move.
        self.agent_index = self.get_next_agent_index()

    def get_agent_position(self, agent_index: int | None = None) -> pacai.core.board.Position | None:
        """ Get the position of the specified agent (or current agent if no agent is specified). """

        if (agent_index is None):
            agent_index = self.agent_index

        if (self.agent_index < 0):
            raise ValueError("No agent is active, cannot get position.")

        return self.board.get_agent_position(self.agent_index)

    def get_agent_last_action(self, agent_index: int | None = None) -> pacai.core.action.Action | None:
        """ Get the last action of the specified agent (or current agent if no agent is specified). """

        if (agent_index is None):
            agent_index = self.agent_index

        if (self.agent_index < 0):
            raise ValueError("No agent is active, cannot get position.")

        return self.last_actions.get(agent_index, None)

    def get_reverse_action(self, action: pacai.core.action.Action) -> pacai.core.action.Action | None:
        """
        Get the reverse of an action, or None if the action has no reverse.
        By default, "reverse" is just defined in terms of cardinal directions.
        However, this method exists so that child games can override this definition of "reverse" if necessary.
        """

        return action.get_reverse_direction()

    def generate_sucessor(self, action: pacai.core.action.Action) -> 'GameState':
        """
        Create a new deep copy of this state that represents the current agent taking the given action.
        To just apply an action to the current state, use process_turn().
        """

        successor = copy.deepcopy(self)
        successor.process_turn(action)

        return successor

    def process_turn(self, action: pacai.core.action.Action) -> None:
        """
        Process the current agent's turn with the given action.
        This will modify the current state to end the current turn and prepare for the next one.
        To get a copy of a potential successor state, use generate_sucessor().
        """

        self._apply_action(action)
        self._finish_turn(action)

    def _finish_turn(self, action: pacai.core.action.Action) -> None:
        """ Perform all the final bookkeeping steps when applying an action. """


        # Track this last action.
        self.last_actions[self.agent_index] = action

        # Issue this agent a new ticket.
        self.tickets[self.agent_index] = self.tickets[self.agent_index].next(self.move_delays[self.agent_index])

        # If the game is not over, pick an agent for the next turn.
        self.agent_index = -1
        if (not self.game_over):
            self.agent_index = self.get_next_agent_index()

        # Increment the move count.
        self.turn_count += 1

    def get_next_agent_index(self) -> int:
        """
        Get the agent that moves next.
        Do this by looking at the agents' tickets and choosing the one with the lowest ticket.
        """

        next_index = -1
        for (agent_index, ticket) in self.tickets.items():
            if ((next_index == -1) or (ticket < self.tickets[next_index])):
                next_index = agent_index

        return next_index

    @abc.abstractmethod
    def get_legal_actions(self) -> list[pacai.core.action.Action]:
        """ Get the moves that the current agent is allowed to make. """

        pass

    @abc.abstractmethod
    def _apply_action(self, action: pacai.core.action.Action) -> None:
        """ Apply the given action to this state. """

        pass
