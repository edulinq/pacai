import abc
import logging
import random

import pacai.core.action
import pacai.core.agent
import pacai.core.isolation
import pacai.core.ui

# TODO(eriq): Clean up the difference between what should be passed in the constructor and run().

class GameResult:
    """ The result of running a game. """

    def __init__(self,
            id: int, seed: int,
            agent_args: list[pacai.core.agent.AgentArguments],
            score: int = 0) -> None:
        """
        Create a new game result.
        This class is mutable and will be modified as the game progresses.
        """

        self.id: int = id
        """ The ID of the game. """

        self.seed: int = seed
        """ The seed used for the game. """

        self.agent_args: list[pacai.core.agent.AgentArguments] = agent_args.copy()
        """ The arguments used to construct each agent. """

        self.history: list[pacai.core.action.ActionRecord] = []
        """ The history of actions taken by each agent in this game. """

        self.score: int = score
        """ The score of the game. """

    def update(self, state: pacai.core.gamestate.GameState, action_record: pacai.core.action.ActionRecord) -> None:
        """ Update the game result after an agent move. """

        self.score = state.score
        self.history.append(action_record)

class Game(abc.ABC):
    """
    A game that can be run in pacai.
    Games combine the rules, layouts, and agents to run.
    """

    def __init__(self,
            agent_args: list[pacai.core.agent.AgentArguments],
            isolation_level: pacai.core.isolation.Level = pacai.core.isolation.Level.NONE,
            max_moves: int = -1,
            seed: int | None = None,
            ) -> None:
        """
        Construct a game.

        Game's only carry nonvolatile information about themselves in member data,
        i.e., they do not carry information about an in-progress game.
        """

        if (seed is None):
            seed = random.randint(0, 2**64)

        self._seed: int = seed
        """ The random seed for this game's RNG. """

        self._agent_args: list[pacai.core.agent.AgentArguments] = agent_args
        """ The required information for creating the agents for this game. """

        if (len(self._agent_args) == 0):
            raise ValueError("No agents provided.")

        self._isolation_level: pacai.core.isolation.Level = isolation_level
        """ The isolation level to use for this game. """

        self._max_moves: int = max_moves
        """
        The total number of moves (between all agents) allowed for this game.
        If -1, unlimited moves are allowed.
        """

    @abc.abstractmethod
    def get_initial_state(self, rng: random.Random, board: pacai.core.board.Board) -> pacai.core.gamestate.GameState:
        """ Create the initial state for this game. """

        pass

    @abc.abstractmethod
    def process_action(self, state: pacai.core.gamestate.GameState, action_record: pacai.core.action.ActionRecord) -> pacai.core.gamestate.GameState:
        """
        Process the given move and return an updated game state.
        The returned game state may be a copy or modified version of the passed in game state.
        """

        pass

    def check_end(self, state: pacai.core.gamestate.GameState) -> bool:
        """
        Check to see if the game is over.
        Return True if the game is now over, False otherwise.

        By default, this will just check pacai.core.gamestate.GameState.game_over,
        but child games can override for more complex functionality.
        """

        return state.game_over

    # TODO(eriq): Validate that the board works for this game (e.g., number of agent positions).

    def run(self, board: pacai.core.board.Board, ui: pacai.core.ui.UI) -> GameResult:
        """
        The main "game loop" for all games.
        One round of the loop will:
         1) allow the next agent to move,
         2) allocate a new ticket for the moved agent,
         3) record actions,
         4) check the game's rules,
         and 5) update the display.
        """

        logging.debug("Starting a game with seed: %d.", self._seed)

        # Create a new random number generator just for this game.
        rng = random.Random(self._seed)

        # Initialize the agent isolator.
        isolator = self._isolation_level.get_isolator()
        isolator.init_agents(self._agent_args)

        # Assign initial tickets to all the agents.
        tickets = []
        for i in range(len(self._agent_args)):
            tickets.append(pacai.core.agent.Ticket(i + self._agent_args[i].move_delay, 0, 0))

        # Keep track of what happens during this game.
        result_id = rng.randint(0, 2**64)
        result = GameResult(result_id, self._seed, self._agent_args)

        # Keep track of all the user inputs since the last time an agent moved.
        # Note that we need to keep track for all agents,
        # since the UI will only tell us the inputs since the last call.
        agent_user_inputs: list[list[pacai.core.action.Action]] = [[] for _ in self._agent_args]

        # Create the initial game state.
        state = self.get_initial_state(rng, board)

        # Notify agents about the start of the game.
        isolator.game_start(rng, state)

        # Start the UI.
        ui.game_start(state)

        move_count = 0
        while ((self._max_moves < 0) or (move_count < self._max_moves)):
            # Choose the next agent to move.
            agent_index = self._get_next_agent_index(tickets)
            state.agent_index = agent_index

            logging.debug("Turn %d, agent %d, state: '%s'.", move_count, agent_index, state)

            # Get any user inputs.
            user_inputs = self._get_user_inputs(agent_index, agent_user_inputs, ui)

            # Get the next action from the agent.
            action_record = isolator.get_action(state, user_inputs)

            # Execute the next action and update the state.
            state = self.process_action(state, action_record)
            state.last_agent_actions[agent_index] = action_record.action
            state.agent_index = -1
            state.turn_count += 1

            # Update the UI.
            ui.update(state)

            # Update the game result and move history.
            result.update(state, action_record)

            # Check for game ending conditions.
            game_over = self.check_end(state)
            if (game_over):
                break

            # Issue the agent a new ticket.
            tickets[agent_index] = tickets[agent_index].next(self._agent_args[agent_index].move_delay)

            # Increment the move count.
            move_count += 1

        # Check if this game ended naturally or in a timeout.
        if (not state.game_over):
            state.timeout = True

        # Notify agents about the end of this game.
        isolator.game_complete(state)

        # Update the UI.
        ui.game_complete(state)

        # Cleanup
        isolator.close()
        ui.close()

        return result

    def _get_next_agent_index(self, tickets: list[pacai.core.agent.Ticket]) -> int:
        """
        Get the agent that moves next.
        Do this by looking at the agents' tickets and choosing the one with the lowest ticket.
        """

        next_index = 0
        for i in range(1, len(tickets)):
            if (tickets[i] < tickets[next_index]):
                next_index = i

        return next_index

    def _get_user_inputs(self, agent_index: int, agent_user_inputs: list[list[pacai.core.action.Action]], ui: pacai.core.ui.UI) -> list[pacai.core.action.Action]:
        """
        Add the current user inputs to the running list for each agent,
        and return (and clear) the inputs for the current agent.
        """

        new_user_inputs = ui.get_user_inputs()

        for user_inputs in agent_user_inputs:
            user_inputs += new_user_inputs

        agent_inputs = agent_user_inputs[agent_index]
        agent_user_inputs[agent_index] = []

        return agent_inputs
