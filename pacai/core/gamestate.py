import copy
import typing

import pacai.core.action
import pacai.core.agentinfo
import pacai.core.board
import pacai.core.ticket
import pacai.util.json

class GameState(pacai.util.json.DictConverter):
    """
    The base for all game states in pacai.
    A game state should contain all the information about the current state of the game.

    Game states should only be interacted with via their methods and not their member variables
    (since this class has been optimized for performance).
    """

    def __init__(self,
            board: pacai.core.board.Board | None = None,
            seed: int = -1,
            agent_index: int = -1,
            game_over: bool = False,
            last_actions: dict[int, pacai.core.action.Action] | None = None,
            score: int = 0,
            turn_count: int = 0,
            move_delays: dict[int, int] | None = None,
            tickets: dict[int, pacai.core.ticket.Ticket] | None = None,
            agent_infos: dict[int, pacai.core.agentinfo.AgentInfo] | None = None,
            **kwargs) -> None:
        if (board is None):
            raise ValueError("Cannot construct a game state without a board.")

        self.board: pacai.core.board.Board = board
        """ The current board. """

        self.seed: int = seed
        """ A utility seed that components using the game state may use to seed their own RNGs. """

        self.agent_index: int = agent_index
        """
        The index of the agent with the current move.
        -1 indicates that the agent to move has not been selected yet.
        """

        self.game_over: bool = game_over
        """ Indicates that this state represents a complete game. """

        if (last_actions is None):
            last_actions = {}

        self.last_actions: dict[int, pacai.core.action.Action] = last_actions
        """ Keep track of the last action that each agent made. """

        self.score: int = score
        """ The current score of the game. """

        self.turn_count: int = turn_count
        """ The number of turns (agent actions) that the game has had. """

        if (move_delays is None):
            move_delays = {}

        self.move_delays: dict[int, int] = move_delays
        """
        The current move delay for each agent.
        Every agent should always have a move delay.
        """

        if (tickets is None):
            tickets = {}

        self.tickets: dict[int, pacai.core.ticket.Ticket] = tickets
        """
        The current ticket for each agent.
        Every agent should always have a ticket once the game starts (even if it is not taking a move).
        """

        # Initialize data from agent arguments if not enough info is provided.
        if ((len(self.move_delays) == 0) and (agent_infos is not None)):
            for (info_agent_index, agent_info) in agent_infos.items():
                self.move_delays[info_agent_index] = agent_info.move_delay

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

    def game_complete(self) -> list[int]:
        """
        Indicate that the game has ended.
        The state should take any final actions and return the indexes of the winning agents (if any).
        """

        return []

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

    def process_agent_crash(self, agent_index: int):
        """
        Notify the state that the given agent has crashed.
        The state should make any updates and set the end of game information.
        """

        self.game_over = True

    def process_game_timeout(self):
        """
        Notify the state that the game has reached the maximum number of turns without ending.
        The state should make any updates and set the end of game information.
        """

        self.game_over = True

    def process_turn(self, action: pacai.core.action.Action) -> None:
        """
        Process the current agent's turn with the given action.
        This will modify the current state.
        To get a copy of a potential successor state, use generate_sucessor().
        """

    def finish_turn(self, action: pacai.core.action.Action) -> None:
        """ Perform all the final bookkeeping steps when a turn is over. """

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
            if ((next_index == -1) or (ticket.is_before(self.tickets[next_index]))):
                next_index = agent_index

        return next_index

    def to_dict(self) -> dict[str, typing.Any]:
        data = vars(self).copy()

        data['board'] = self.board.to_dict()
        data['last_actions'] = {agent_index: str(action) for (agent_index, action) in sorted(self.last_actions.items())}
        data['tickets'] = {agent_index: ticket.to_dict() for (agent_index, ticket) in sorted(self.tickets.items())}

        return data

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        data = data.copy()

        data['board'] = pacai.core.board.Board.from_dict(data['board'])
        data['last_actions'] = {int(agent_index): pacai.core.action.Action(action) for (agent_index, action) in data['last_actions'].items()}
        data['tickets'] = {int(agent_index): pacai.core.ticket.Ticket.from_dict(ticket) for (agent_index, ticket) in data['tickets'].items()}

        return cls(**data)

    def get_legal_actions(self) -> list[pacai.core.action.Action]:
        """ Get the moves that the current agent is allowed to make. """

        return []

@typing.runtime_checkable
class EvaluationFunction(typing.Protocol):
    """
    A function that can be used to score a game state.
    """

    def __call__(self,
            state: GameState,
            action: pacai.core.action.Action | None = None,
            old_state: GameState | None = None,
            ) -> float:
        """
        Compute a score for a state that an agent can use to decide actions.
        The current state is the only required argument, the others are optional.
        """

def base_eval(
        state: GameState,
        action: pacai.core.action.Action | None = None,
        old_state: GameState | None = None,
        ) -> float:
    """ The most basic evaluation function, which just uses the state's current score. """

    return float(state.score)
