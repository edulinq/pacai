import abc
import argparse
import copy
import logging
import os
import random
import typing

import pacai.core.action
import pacai.core.agentaction
import pacai.core.agentinfo
import pacai.core.isolation.level
import pacai.core.ui
import pacai.util.json

DEFAULT_MAX_TURNS: int = -1
DEFAULT_AGENT: str = 'pacai.agents.random.RandomAgent'

class GameInfo(pacai.util.json.DictConverter):
    """
    A simple container that holds common information about a game.
    """

    def __init__(self,
            board_source: str,
            agent_infos: dict[int, pacai.core.agentinfo.AgentInfo],
            isolation_level: pacai.core.isolation.level.Level = pacai.core.isolation.level.Level.NONE,
            max_turns: int = DEFAULT_MAX_TURNS,
            seed: int | None = None,
            ) -> None:
        if (seed is None):
            seed = random.randint(0, 2**64)

        self.seed: int = seed
        """ The random seed for this game's RNG. """

        self.board_source: str = board_source
        """ Where the board from this game is loaded from. """

        self.agent_infos: dict[int, pacai.core.agentinfo.AgentInfo] = agent_infos
        """ The required information for creating the agents for this game. """

        if (len(self.agent_infos) == 0):
            raise ValueError("No agents provided.")

        self.isolation_level: pacai.core.isolation.level.Level = isolation_level
        """ The isolation level to use for this game. """

        self.max_turns: int = max_turns
        """
        The total number of moves (between all agents) allowed for this game.
        If -1, unlimited moves are allowed.
        """

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'seed': self.seed,
            'board_source': self.board_source,
            'agent_infos': {id: info.to_dict() for (id, info) in self.agent_infos.items()},
            'isolation_level': self.isolation_level.value,
            'max_turns': self.max_turns,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        return GameInfo(
            seed = data.get('seed', None),
            board_source = data['board_source'],
            agent_infos = {int(id): pacai.core.agentinfo.AgentInfo.from_dict(raw_info) for (id, raw_info) in data['agent_infos'].items()},
            isolation_level = pacai.core.isolation.level.Level(data.get('isolation_level', pacai.core.isolation.level.Level.NONE.value)),
            max_turns = data.get('max_turns', DEFAULT_MAX_TURNS))

class GameResult(pacai.util.json.DictConverter):
    """ The result of running a game. """

    def __init__(self,
            game_id: int,
            game_info: GameInfo,
            score: int = 0,
            winning_agent_index: int = -1,
            start_time: pacai.util.time.Timestamp | None = None,
            end_time: pacai.util.time.Timestamp | None = None,
            history: list[pacai.core.agentaction.AgentActionRecord] | None = None,
            **kwargs) -> None:
        self.game_id: int = game_id
        """ The ID of the game result. """

        self.game_info: GameInfo = game_info
        """ The core information about this game. """

        if (start_time is None):
            start_time = pacai.util.time.now()

        self.start_time = start_time
        """ The time the game started at. """

        self.end_time = end_time
        """ The time the game ended at. """

        if (history is None):
            history = []

        self.history: list[pacai.core.agentaction.AgentActionRecord] = history
        """ The history of actions taken by each agent in this game. """

        self.score: int = score
        """ The score of the game. """

        self.winning_agent_index: int = winning_agent_index
        """
        The agent that is considered the "winner" of this game.
        Games may interpret this value in different ways.
        """

    def update(self,
            state: pacai.core.gamestate.GameState,
            action_record: pacai.core.agentaction.AgentActionRecord,
            ) -> None:
        """ Update the game result after an agent move. """

        self.score = state.score
        self.history.append(action_record)

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'game_id': self.game_id,
            'game_info': self.game_info.to_dict(),
            'start_time': self.start_time,
            'end_time': self.end_time,
            'history': [item.to_dict() for item in self.history],
            'score': self.score,
            'winning_agent_index': self.winning_agent_index,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        return cls(
            data['game_id'],
            GameInfo.from_dict(data['game_info']),
            start_time = data.get('start_time', None),
            end_time = data.get('end_time', None),
            history = [pacai.core.agentaction.AgentActionRecord.from_dict(item) for item in data.get('history', [])],
            score = data.get('score', 0),
            winning_agent_index = data.get('winning_agent_index', -1),
        )

class Game(abc.ABC):
    """
    A game that can be run in pacai.
    Games combine the rules, layouts, and agents to run.
    """

    def __init__(self,
            game_info: GameInfo,
            board: pacai.core.board.Board,
            save_path: str | None = None,
            is_replay: bool = False,
            ) -> None:
        self._game_info: GameInfo = game_info
        """ The core information about this game. """

        self._board: pacai.core.board.Board = board
        """ The board this game will be played on. """

        self._save_path: str | None = save_path
        """ Where to save the results of this game. """

        self._is_replay: bool = is_replay
        """
        Indicates that this game is being loaded from a replay.
        Some behavior, like saving the result, will be modified.
        """

    @abc.abstractmethod
    def get_initial_state(self,
            rng: random.Random,
            board: pacai.core.board.Board,
            agent_infos: dict[int, pacai.core.agentinfo.AgentInfo],
            ) -> pacai.core.gamestate.GameState:
        """ Create the initial state for this game. """

    def process_turn(self,
            state: pacai.core.gamestate.GameState,
            action_record: pacai.core.agentaction.AgentActionRecord,
            ) -> pacai.core.gamestate.GameState:
        """
        Process the given move and return an updated game state.
        The returned game state may be a copy or modified version of the passed in game state.
        """

        action = action_record.get_action()
        if (action not in state.get_legal_actions()):
            raise ValueError(f"Illegal action for agent {state.agent_index}: '{action}'.")

        state.process_turn(action)
        return state

    def check_end(self, state: pacai.core.gamestate.GameState) -> bool:
        """
        Check to see if the game is over.
        Return True if the game is now over, False otherwise.

        By default, this will just check pacai.core.gamestate.GameState.game_over,
        but child games can override for more complex functionality.
        """

        return state.game_over

    def game_complete(self, state: pacai.core.gamestate.GameState, result: GameResult) -> None:
        """
        Make any last adjustments to the game result after the game is over.
        """

    def run(self, ui: pacai.core.ui.UI) -> GameResult:
        """
        The main "game loop" for all games.
        """

        logging.debug("Starting a game with seed: %d.", self._game_info.seed)

        # Create a new random number generator just for this game.
        rng = random.Random(self._game_info.seed)

        # Initialize the agent isolator.
        isolator = self._game_info.isolation_level.get_isolator()
        isolator.init_agents(self._game_info.agent_infos)

        # Keep track of what happens during this game.
        game_id = rng.randint(0, 2**64)
        result = GameResult(game_id, self._game_info)

        # Keep track of all the user inputs since the last time an agent moved.
        # Note that we need to keep track for all agents,
        # since the UI will only tell us the inputs since the last call.
        agent_user_inputs: dict[int, list[pacai.core.action.Action]] = {}
        for agent_index in self._game_info.agent_infos:
            agent_user_inputs[agent_index] = []

        # Create the initial game state.
        state = self.get_initial_state(rng, self._board, self._game_info.agent_infos)
        state.game_start()

        board_highlights: list[pacai.core.board.Highlight] = []

        # Notify agents about the start of the game.
        records = isolator.game_start(rng, state)
        for record in records.values():
            board_highlights += record.get_board_highlights()

        # Start the UI.
        ui.game_start(state, board_highlights = board_highlights)

        while ((self._game_info.max_turns < 0) or (state.turn_count < self._game_info.max_turns)):
            logging.debug("Turn %d, agent %d.", state.turn_count, state.agent_index)

            # Get any user inputs.
            user_inputs = self._get_user_inputs(state.agent_index, agent_user_inputs, ui)

            # Get the next action from the agent.
            action_record = isolator.get_action(state, user_inputs)

            # TODO(eriq): Handle crashes -- acton_record.agent_action is None

            # Execute the next action and update the state.
            state = self.process_turn(state, action_record)

            # Update the UI.
            ui.update(state, board_highlights = action_record.get_board_highlights())

            # Update the game result and move history.
            result.update(state, action_record)

            # Check for game ending conditions.
            game_over = self.check_end(state)
            if (game_over):
                break

        # Check if this game ended naturally or in a timeout.
        if (not state.game_over):
            state.game_over = True

            # Don't count replays as timeouts.
            if (not self._is_replay):
                state.timeout = True

        # Mark the end time of the game.
        result.end_time = pacai.util.time.now()

        # Notify agents about the end of this game.
        isolator.game_complete(state)

        # All the game to make final updates to the result.
        self.game_complete(state, result)

        # Update the UI.
        ui.game_complete(state)

        # Cleanup
        isolator.close()
        ui.close()

        if ((not self._is_replay) and (self._save_path is not None)):
            logging.info("Saving results to '%s'.", self._save_path)
            pacai.util.json.dump_path(result, self._save_path)

        return result

    def _get_user_inputs(self,
            agent_index: int,
            agent_user_inputs: dict[int, list[pacai.core.action.Action]],
            ui: pacai.core.ui.UI,
            ) -> list[pacai.core.action.Action]:
        """
        Add the current user inputs to the running list for each agent,
        and return (and clear) the inputs for the current agent.
        """

        new_user_inputs = ui.get_user_inputs()

        for user_inputs in agent_user_inputs.values():
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

    parser.add_argument('--num-games', dest = 'num_games',
            action = 'store', type = int, default = 1,
            help = 'The number of games to play (default: %(default)s).')

    parser.add_argument('--seed', dest = 'seed',
            action = 'store', type = int, default = None,
            help = 'The random seed for the game (will be randomly generated if not set.')

    parser.add_argument('--max-turns', dest = 'max_turns',
            action = 'store', type = int, default = DEFAULT_MAX_TURNS,
            help = 'The maximum number of turns/moves (total for all agents) allowed in this game (-1 for unlimited) (default: %(default)s).')

    parser.add_argument('--isolation', dest = 'isolation_level', metavar = 'LEVEL',
            action = 'store', type = str, default = pacai.core.isolation.level.Level.NONE.value,
            choices = pacai.core.isolation.level.LEVELS,
            help = ('Set the agent isolation level for this game (default: %(default)s).'
                    + ' Choose one of:'
                    + ' `none` -- Do not make any attempt to isolate the agent code from the game (fastest and least secure),'
                    + ' `process` -- Run the agent code in a separate process'
                    + ' (offers some protection, but still vulnerable to disk or execution exploits),'
                    + ' `tcp` -- Open TCP listeners to communicate with agents (most secure, requires additional work to set up agents).'))

    parser.add_argument('--agent-arg', dest = 'raw_agent_args', metavar = 'ARG',
            action = 'append', type = str, default = [],
            help = ('Specify arguments directly to agents (may be used multiple times).'
                    + ' The value for this argument must be formatted as "agent_index::key=value",'
                    + ' for example to set `foo = 9` for agent 3 and `bar = a` for agent 2, we can use:'
                    + ' `--agent-arg 3::foo=9 --agent-arg 1::bar=a`.'))

    parser.add_argument('--remove-agent', dest = 'remove_agent_indexes', metavar = 'AGENT_INDEX',
            action = 'append', type = int, default = [],
            help = 'Remove this agent from the board before starting (may be used multiple times).')

    parser.add_argument('--save-path', dest = 'save_path',
            action = 'store', type = str, default = None,
            help = ('If specified, write the result of this game to the specified location.'
                    + ' This file can be replayed with `--replay-path`.'))

    parser.add_argument('--replay-path', dest = 'replay_path',
            action = 'store', type = str, default = None,
            help = 'If specified, replay the game whose result was saved at the specified path with `--save-path`.')

def init_from_args(
        args: argparse.Namespace,
        game_class: typing.Type[Game],
        base_agent_infos: dict[int, pacai.core.agentinfo.AgentInfo] | None = None,
        remove_agent_indexes: list[int] | None = None) -> argparse.Namespace:
    """
    Take in args from a parser that was passed to set_cli_args(),
    and initialize the proper components.
    This will create a number of games (and related resources) depending on `--num-games`.
    Each of these resources will be placed in their respective list at
    `args._boards`, `args._agent_infos`, or `args._games`.
    """

    if (base_agent_infos is None):
        base_agent_infos = {}

    if (remove_agent_indexes is None):
        remove_agent_indexes = []

    # If this is a replay,
    # then all the core arguments are loaded differently (directly from the file).
    # Use the replay file to override all the current options.
    if (args.replay_path is not None):
        _override_args_with_replay(args, base_agent_infos)
        remove_agent_indexes = []

    if (args.board is None):
        raise ValueError("No board was specified.")

    if (args.num_games <= 0):
        raise ValueError(f"At least one game must be played, {args.num_games} was specified.")

    # Establish an RNG to generate seeds for each game using the given seed.
    seed = args.seed
    if (seed is None):
        seed = random.randint(0, 2**64)

    rng = random.Random(seed)

    board = pacai.core.board.load_path(args.board)

    # Remove specified agents from the board.
    remove_agent_indexes += args.remove_agent_indexes
    for remove_agent_index in remove_agent_indexes:
        board.remove_agent(remove_agent_index)

    agent_infos = _parse_agent_infos(board.agent_indexes(), args.raw_agent_args, base_agent_infos, remove_agent_indexes)

    base_save_path = args.save_path

    all_boards = []
    all_agent_infos = []
    all_games = []

    for i in range(args.num_games):
        game_seed = rng.randint(0, 2**64)

        all_boards.append(copy.deepcopy(board))
        all_agent_infos.append(copy.deepcopy(agent_infos))

        game_info = GameInfo(
                board.source,
                all_agent_infos[-1],
                isolation_level = pacai.core.isolation.level.Level(args.isolation_level),
                max_turns = args.max_turns,
                seed = game_seed
        )

        # Suffix the save path if there is more than one game.
        save_path = base_save_path
        if ((save_path is not None) and (args.num_games > 1)):
            parts = os.path.splitext(save_path)
            save_path = f"{parts[0]}_{i:03d}{parts[1]}"

        game_args = {
            'game_info': game_info,
            'board': all_boards[-1],
            'save_path': save_path,
        }

        all_games.append(game_class(**game_args))

    setattr(args, '_boards', all_boards)
    setattr(args, '_agent_infos', all_agent_infos)
    setattr(args, '_games', all_games)

    return args

def _override_args_with_replay(args: argparse.Namespace, base_agent_infos: dict[int, pacai.core.agentinfo.AgentInfo]) -> None:
    """
    Override the args with the settings from the replay in the args.
    """

    logging.info("Loading replay from '%s'.", args.replay_path)
    replay_info = typing.cast(GameResult, pacai.util.json.load_object_path(args.replay_path, GameResult))

    # Overrides from the replay info.
    args.board = replay_info.game_info.board_source
    args.seed = replay_info.game_info.seed

    # Special settings for replays.
    args.num_games = 1
    args.max_turns = len(replay_info.history)

    # Script the moves for each agent based on the replay's history.
    scripted_actions: dict[int, list[pacai.core.action.Action]] = {}
    for item in replay_info.history:
        if (item.agent_index not in scripted_actions):
            scripted_actions[item.agent_index] = []

        scripted_actions[item.agent_index].append(item.get_action())

    base_agent_infos.clear()

    for (agent_index, actions) in scripted_actions.items():
        base_agent_infos[agent_index] = pacai.core.agentinfo.AgentInfo(
            name = 'pacai.agents.scripted.ScriptedAgent',
            move_delay = replay_info.game_info.agent_infos[agent_index].move_delay,
            actions = actions,
        )

def _parse_agent_infos(
        agent_indexes: list[int],
        raw_args: list[str],
        base_agent_infos: dict[int, pacai.core.agentinfo.AgentInfo],
        remove_agent_indexes: list[int]) -> dict[int, pacai.core.agentinfo.AgentInfo]:
    # Initialize with random agents.
    agent_info = {agent_index: pacai.core.agentinfo.AgentInfo(name = DEFAULT_AGENT) for agent_index in sorted(agent_indexes)}

    # Take any args from the base args.
    for (agent_index, base_agent_info) in base_agent_infos.items():
        if (agent_index in agent_info):
            agent_info[agent_index].update(base_agent_info)

    # Update with CLI args.
    for raw_arg in raw_args:
        raw_arg = raw_arg.strip()
        if (len(raw_arg) == 0):
            continue

        parts = raw_arg.split('::', 1)
        if (len(parts) != 2):
            raise ValueError(f"Improperly formatted CLI agent argument: '{raw_arg}'.")

        agent_index = int(parts[0])
        if (agent_index not in agent_info):
            raise ValueError(f"CLI agent argument has an unknown agent index: {agent_index}.")

        raw_pair = parts[1]

        parts = raw_pair.split('=', 1)
        if (len(parts) != 2):
            raise ValueError(f"Improperly formatted CLI agent argument key/value pair: '{raw_pair}'.")

        key = parts[0].strip()
        value = parts[1].strip()

        agent_info[agent_index].set(key, value)

    # Remove specified agents.
    for remove_agent_index in remove_agent_indexes:
        if (remove_agent_index in agent_info):
            del agent_info[remove_agent_index]

    return agent_info
