import copy
import random
import typing

import PIL.Image
import edq.util.json

import pacai.core.action
import pacai.core.agentaction
import pacai.core.agentinfo
import pacai.core.board
import pacai.core.font
import pacai.core.spritesheet
import pacai.core.ticket
import pacai.util.math

class GameState(edq.util.json.DictConverter):
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
            agent_actions: dict[int, list[pacai.core.action.Action]] | None = None,
            score: float = 0,
            turn_count: int = 0,
            move_delays: dict[int, int] | None = None,
            tickets: dict[int, pacai.core.ticket.Ticket] | None = None,
            agent_infos: dict[int, pacai.core.agentinfo.AgentInfo] | None = None,
            **kwargs: typing.Any) -> None:
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

        self.last_agent_index: int = -1
        """
        The index of the agent who just moved.
        -1 indicates that no move has been made yet.
        """

        self.game_over: bool = game_over
        """ Indicates that this state represents a complete game. """

        if (agent_actions is None):
            agent_actions = {}

        self.agent_actions: dict[int, list[pacai.core.action.Action]] = agent_actions
        """ Keep track of the actions that each agent makes. """

        self.score: float = score
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

    def copy(self) -> 'GameState':
        """
        Get a deep copy of this state.

        Child classes are responsible for making any deep copies they need to.
        """

        new_state = copy.copy(self)

        new_state.board = self.board.copy()
        new_state.agent_actions = {agent_index: actions.copy() for (agent_index, actions) in self.agent_actions.items()}
        new_state.move_delays = self.move_delays.copy()
        new_state.tickets = self.tickets.copy()

        return new_state

    def game_start(self) -> None:
        """
        Indicate that the game is starting.
        This will initialize some state like tickets.
        """

        # Issue initial tickets.
        for agent_index in self.move_delays.keys():
            self.tickets[agent_index] = pacai.core.ticket.Ticket(agent_index + self.compute_move_delay(agent_index), 0, 0)

        # Choose the first agent to move.
        self.last_agent_index = self.agent_index
        self.agent_index = self.get_next_agent_index()

    def agents_game_start(self, agent_responses: dict[int, pacai.core.agentaction.AgentActionRecord]) -> None:
        """ Indicate that agents have been started. """

    def game_complete(self) -> list[int]:
        """
        Indicate that the game has ended.
        The state should take any final actions and return the indexes of the winning agents (if any).
        """

        return []

    def get_num_agents(self) -> int:
        """ Get the number of agents this state is tracking. """

        return len(self.tickets)

    def get_agent_indexes(self) -> list[int]:
        """ Get the index of all agents tracked by this game state. """

        return list(sorted(self.tickets.keys()))

    def get_agent_positions(self) -> dict[int, pacai.core.board.Position | None]:
        """
        Get the positions of all agents.
        If an agent is tracked by the game state but not on the board, it will have a None value.
        """

        positions: dict[int, pacai.core.board.Position | None] = {}
        for agent_index in self.tickets:
            positions[agent_index] = self.get_agent_position(agent_index)

        return positions

    def get_agent_position(self, agent_index: int | None = None) -> pacai.core.board.Position | None:
        """ Get the position of the specified agent (or current agent if no agent is specified). """

        if (agent_index is None):
            agent_index = self.agent_index

        if (agent_index < 0):
            raise ValueError("No agent is active, cannot get position.")

        return self.board.get_agent_position(agent_index)

    def get_agent_actions(self, agent_index: int | None = None) -> list[pacai.core.action.Action]:
        """ Get the previous actions of the specified agent (or current agent if no agent is specified). """

        if (agent_index is None):
            agent_index = self.agent_index

        if (agent_index < 0):
            return []

        if (agent_index not in self.agent_actions):
            self.agent_actions[agent_index] = []

        return self.agent_actions[agent_index]

    def get_last_agent_action(self, agent_index: int | None = None) -> pacai.core.action.Action | None:
        """ Get the last action of the specified agent (or current agent if no agent is specified). """

        actions = self.get_agent_actions(agent_index)
        if (len(actions) == 0):
            return None

        return actions[-1]

    def get_reverse_action(self, action: pacai.core.action.Action | None) -> pacai.core.action.Action | None:
        """
        Get the reverse of an action, or None if the action has no reverse.
        By default, "reverse" is just defined in terms of cardinal directions.
        However, this method exists so that child games can override this definition of "reverse" if necessary.
        """

        if (action is None):
            return None

        return pacai.core.action.get_reverse_direction(action)

    def generate_successor(self,
            action: pacai.core.action.Action,
            rng: random.Random | None = None,
            **kwargs: typing.Any) -> 'GameState':
        """
        Create a new deep copy of this state that represents the current agent taking the given action.
        To just apply an action to the current state, use process_turn().
        """

        successor = self.copy()
        successor.process_turn_full(action, rng, **kwargs)

        return successor

    def process_agent_timeout(self, agent_index: int) -> None:
        """
        Notify the state that the given agent has timed out.
        The state should make any updates and set the end of game information.
        """

        self.game_over = True

    def process_agent_crash(self, agent_index: int) -> None:
        """
        Notify the state that the given agent has crashed.
        The state should make any updates and set the end of game information.
        """

        self.game_over = True

    def process_game_timeout(self) -> None:
        """
        Notify the state that the game has reached the maximum number of turns without ending.
        The state should make any updates and set the end of game information.
        """

        self.game_over = True

    def process_turn(self,
            action: pacai.core.action.Action,
            rng: random.Random | None = None,
            **kwargs: typing.Any) -> None:
        """
        Process the current agent's turn with the given action.
        This may modify the current state.
        To get a copy of a potential successor state, use generate_successor().
        """

    def process_turn_full(self,
            action: pacai.core.action.Action,
            rng: random.Random | None = None,
            **kwargs: typing.Any) -> None:
        """
        Process the current agent's turn with the given action.
        This will modify the current state.
        First procecss_turn() will be called,
        then any bookkeeping will be performed.
        Child classes should prefer overriding the simpler process_turn().

        To get a copy of a potential successor state, use generate_successor().
        """

        # If the game is over, don't do anyhting.
        # This case can come up when planning agent actions and generating successors.
        if (self.game_over):
            return

        self.process_turn(action, rng, **kwargs)

        # Track this last action.
        if (self.agent_index not in self.agent_actions):
            self.agent_actions[self.agent_index] = []

        self.agent_actions[self.agent_index].append(action)

        # Issue this agent a new ticket.
        self.tickets[self.agent_index] = self.tickets[self.agent_index].next(self.compute_move_delay(self.agent_index))

        # If the game is not over, pick an agent for the next turn.
        self.last_agent_index = self.agent_index
        self.agent_index = -1
        if (not self.game_over):
            self.agent_index = self.get_next_agent_index()

        # Increment the move count.
        self.turn_count += 1

    def compute_move_delay(self, agent_index: int) -> int:
        """
        The the current move delay for the agent.
        By default, this just looks up the value in self.move_delays.
        However, this method allows children to implement move complex functionality
        (e.g., power-ups that affect an agent's speed).
        """

        return self.move_delays[agent_index]

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

    def sprite_lookup(self,
            sprite_sheet: pacai.core.spritesheet.SpriteSheet,
            position: pacai.core.board.Position,
            marker: pacai.core.board.Marker | None = None,
            action: pacai.core.action.Action | None = None,
            adjacency: pacai.core.board.AdjacencyString | None = None,
            animation_key: str | None = None,
            ) -> PIL.Image.Image:
        """
        Lookup the proper sprite for a situation.
        By default this just calls into the sprite sheet,
        but children may override for more expressive functionality.
        """

        return sprite_sheet.get_sprite(marker = marker, action = action, adjacency = adjacency, animation_key = animation_key)

    def skip_draw(self,
            marker: pacai.core.board.Marker,
            position: pacai.core.board.Position,
            static: bool = False,
            ) -> bool:
        """ Return true if this marker/position combination should not be drawn on the board. """

        return False

    def get_static_positions(self) -> list[pacai.core.board.Position]:
        """ Get a list of positions to draw on the board statically. """

        return []

    def get_static_text(self) -> list[pacai.core.font.BoardText]:
        """ Get any static text to display on board positions. """

        return []

    def get_nonstatic_text(self) -> list[pacai.core.font.BoardText]:
        """ Get any non-static text to display on board positions. """

        return []

    def get_footer_text(self) -> pacai.core.font.Text | None:
        """
        Get any text to draw in the UI's footer.
        By default, this will return the score.
        """

        score_text = f" Score: {pacai.util.math.display_number(self.score, places = 2)}"
        if (self.game_over):
            score_text += " - Final"

        return pacai.core.font.Text(score_text, horizontal_align = pacai.core.font.TextHorizontalAlign.LEFT)

    def to_dict(self) -> dict[str, typing.Any]:
        data = vars(self).copy()

        data['board'] = self.board.to_dict()
        data['tickets'] = {agent_index: ticket.to_dict() for (agent_index, ticket) in sorted(self.tickets.items())}
        data['agent_actions'] = {agent_index: [str(action) for action in actions] for (agent_index, actions) in self.agent_actions.items()}

        return data

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        data = data.copy()

        data['board'] = pacai.core.board.Board.from_dict(data['board'])
        data['tickets'] = {int(agent_index): pacai.core.ticket.Ticket.from_dict(ticket) for (agent_index, ticket) in data['tickets'].items()}
        data['agent_actions'] = {int(agent_index): [pacai.core.action.Action(raw_action, safe = True) for raw_action in raw_actions]
                for (agent_index, raw_actions) in data['agent_actions'].items()}

        return cls(**data)

    def get_legal_actions(self, position: pacai.core.board.Position | None = None) -> list[pacai.core.action.Action]:
        """
        Get the moves that the current agent is allowed to make.
        Stopping is generally always considered a legal action (unless a game re-defines this behavior).

        If a position is provided, it will override the current agent's position.
        """

        # Stopping is generally safe.
        actions = [pacai.core.action.STOP]

        if (position is None):
            if (self.agent_index == -1):
                raise ValueError("Cannot get legal actions when no agent is active.")

            position = self.get_agent_position()

            # If the agent is not on the board, it can only stop.
            if (position is None):
                return actions

        # Get moves to adjacent positions.
        neighbor_moves = self.board.get_neighbors(position)
        for (action, _) in neighbor_moves:
            actions.append(action)

        return actions

@typing.runtime_checkable
class AgentStateEvaluationFunction(typing.Protocol):
    """
    A function that can be used to score a game state.
    """

    def __call__(self,
            state: GameState,
            agent: typing.Any | None = None,
            action: pacai.core.action.Action | None = None,
            **kwargs: typing.Any) -> float:
        """
        Compute a score for a state that the provided agent can use to decide actions.
        The current state is the only required argument, the others are optional.
        Passing the agent asking for this evaluation is a simple way to pass persistent state
        (like pre-computed distances) from the agent to this function.
        """

def base_eval(
        state: GameState,
        agent: typing.Any | None = None,
        action: pacai.core.action.Action | None = None,
        **kwargs: typing.Any) -> float:
    """ The most basic evaluation function, which just uses the state's current score. """

    return float(state.score)
