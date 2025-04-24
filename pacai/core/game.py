import abc
import argparse
import logging
import random
import typing

import pacai.core.action
import pacai.core.agent
import pacai.core.isolation
import pacai.core.ui

DEFAULT_MAX_MOVES: int = -1
DEFAULT_AGENT: str = 'pacai.agents.random.RandomAgent'

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
            board: pacai.core.board.Board,
            agent_args: list[pacai.core.agent.AgentArguments],
            isolation_level: pacai.core.isolation.Level = pacai.core.isolation.Level.NONE,
            max_moves: int = DEFAULT_MAX_MOVES,
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

        self._board: pacai.core.board.Board = board
        """ The board this game will be played on. """

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

    def run(self, ui: pacai.core.ui.UI) -> GameResult:
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
        state = self.get_initial_state(rng, self._board)

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

def set_cli_args(parser: argparse.ArgumentParser, default_board: str | None = None) -> None:
    """
    Set common CLI arguments.
    This is a sibling to init_from_args(), as the arguments set here can be interpreted there.
    """

    parser.add_argument('--board', dest = 'board',
            action = 'store', type = str, default = default_board,
            help = ('Play on this board (default: %(default)s).'
                    + ' This may be the full path to a board, or just a filename.'
                    + ' If just a filename, than the `pacai/resources/boards` directory will be checked (using a ".board" extension.'))

    parser.add_argument('--seed', dest = 'seed',
            action = 'store', type = int, default = None,
            help = 'The random seed for the game (will be randomly generated if not set.')

    parser.add_argument('--max-moves', dest = 'max_moves',
            action = 'store', type = int, default = DEFAULT_MAX_MOVES,
            help = 'The maximum number of moves (total for all agents) allowed in this game (-1 for unlimited) (default: %(default)s).')

    parser.add_argument('--isolation', dest = 'isolation_level', metavar = 'LEVEL',
            action = 'store', type = str, default = pacai.core.isolation.Level.NONE.value,
            choices = pacai.core.isolation.LEVELS,
            help = ('Set the agent isolation level for this game (default: %(default)s).'
                    + ' Choose one of:'
                    + ' `none` -- Do not make any attempt to isolate the agent code from the game (fastest and least secure),'
                    + ' `process` -- Run the agent code in a separate process/memory space (offers some protection, but still vulnerable to disk or execution exploits),'
                    + ' `tcp` -- Open TCP listeners to communicate with agents (most secure, requires additional work to set up agents).'))

    parser.add_argument('--agent-args', dest = 'agent_args',
            action = 'append', type = str, default = [],
            help = ('Specify arguments directly to agents.'
                    + ' The value for this argument must be formatted as "agent_index::key=value[,key=value]",'
                    + ' for example to set `foo = 1` and `bar = a` for agent 2, we can use:'
                    + ' `--agent-args 2::foo=1,bar=a`.'
                    + ' This command may be repeated multiple time (for the same or different agents).'))

    ''' TODO(eriq)
    parser.add_argument('--save-path', dest = 'save_path',
            action = 'store', type = str, default = None,
            help = 'If specified, write the result of this game to the specified location.')
    '''

    ''' TODO(eriq)
    parser.add_argument('--replay-path', dest = 'replay_path',
            action = 'store', type = str, default = None,
            help = 'If specified, replay the game whose result was saved at the specified path with `--save-path`.')
    '''

def init_from_args(args: argparse.Namespace, game_class: typing.Type[Game], base_agent_args: list[pacai.core.agent.AgentArguments | None] = []) -> argparse.Namespace:
    """
    Take in args from a parser that was passed to set_cli_args(),
    and initialize the proper components.
    A constructed UI will be placed in the `args._ui`.
    """

    if (args.board is None):
        raise ValueError("No board was specified.")

    board = pacai.core.board.load_path(args.board)
    agent_args = _parse_agent_args(board.agent_count(), args.agent_args, base_agent_args)

    game_args = {
        'board': board,
        'agent_args': agent_args,
        'isolation_level': pacai.core.isolation.Level(args.isolation_level),
        'max_moves': args.max_moves,
        'seed': args.seed,
    }

    game = game_class(**game_args)

    setattr(args, '_board', board)
    setattr(args, '_agent_args', agent_args)
    setattr(args, '_game', game)

    return args

def _parse_agent_args(num_agents: int, raw_args: list[str], base_agent_args: list[pacai.core.agent.AgentArguments | None] = []) -> list[pacai.core.agent.AgentArguments]:
    # Initialize with random agents.
    agent_args = [pacai.core.agent.AgentArguments(name = DEFAULT_AGENT) for _ in range(num_agents)]

    # Take any args from the base args.
    for i in range(min(len(base_agent_args), num_agents)):
        base_agent_arg = base_agent_args[i]
        if (base_agent_arg is not None):
            agent_args[i].update(base_agent_arg)

    # Update with CLI args.
    for raw_arg in raw_args:
        raw_arg = raw_arg.strip()
        if (len(raw_arg) == 0):
            continue

        parts = raw_arg.split('::', 1)
        if (len(parts) != 2):
            raise ValueError(f"Improperly formatted CLI agent argument: '{raw_arg}'.")

        agent_index = int(parts[0])
        if (agent_index >= len(agent_args)):
            raise ValueError(f"CLI agent argument has an out-of-bounds agent index. Found {agent_index}, max {len(agent_args)}.")

        args = parts[1]
        for arg in args.split(','):
            parts = arg.split('=', 1)
            if (len(parts) != 2):
                raise ValueError(f"Improperly formatted CLI agent argument key/value: '{arg}'.")

            key = parts[0].strip()
            value = parts[1].strip()

            agent_args[agent_index].set(key, value)

    return agent_args
