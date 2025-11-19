import abc
import argparse
import copy
import logging
import math
import os
import random
import typing

import edq.util.json

import pacai.core.action
import pacai.core.agentaction
import pacai.core.agentinfo
import pacai.core.isolation.level
import pacai.core.ui
import pacai.util.alias

DEFAULT_MAX_TURNS: int = -1
DEFAULT_AGENT_START_TIMEOUT: float = 0.0
DEFAULT_AGENT_END_TIMEOUT: float = 0.0
DEFAULT_AGENT_ACTION_TIMEOUT: float = 0.0

DEFAULT_AGENT: str = pacai.util.alias.AGENT_RANDOM.short

class GameInfo(edq.util.json.DictConverter):
    """
    A simple container that holds common information about a game.
    """

    def __init__(self,
            board_source: str,
            agent_infos: dict[int, pacai.core.agentinfo.AgentInfo],
            isolation_level: pacai.core.isolation.level.Level = pacai.core.isolation.level.Level.NONE,
            max_turns: int = DEFAULT_MAX_TURNS,
            agent_start_timeout: float = DEFAULT_AGENT_START_TIMEOUT,
            agent_end_timeout: float = DEFAULT_AGENT_END_TIMEOUT,
            agent_action_timeout: float = DEFAULT_AGENT_ACTION_TIMEOUT,
            seed: int | None = None,
            training: bool = False,
            extra_info: dict[str, typing.Any] | None = None,
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

        self.agent_start_timeout: float = agent_start_timeout
        """
        The maximum number of seconds an agent is allowed when starting a game.
        If <= 0, unlimited time is allowed.
        """

        self.agent_end_timeout: float = agent_end_timeout
        """
        The maximum number of seconds an agent is allowed when ending a game.
        If <= 0, unlimited time is allowed.
        """

        self.agent_action_timeout: float = agent_action_timeout
        """
        The maximum number of seconds an agent is allowed when getting an action.
        If <= 0, unlimited time is allowed.
        """

        self.training: bool = training
        """ Whether this game is meant for training agents. """

        if (extra_info is None):
            extra_info = {}

        self.extra_info: dict[str, typing.Any] = extra_info
        """ Any additional arguments passed to the game. """

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'seed': self.seed,
            'board_source': self.board_source,
            'agent_infos': {id: info.to_dict() for (id, info) in self.agent_infos.items()},
            'isolation_level': self.isolation_level.value,
            'max_turns': self.max_turns,
            'agent_start_timeout': self.agent_start_timeout,
            'agent_end_timeout': self.agent_end_timeout,
            'agent_action_timeout': self.agent_action_timeout,
            'training': self.training,
            'extra_info': self.extra_info,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        return cls(
            seed = data.get('seed', None),
            board_source = data['board_source'],
            agent_infos = {int(id): pacai.core.agentinfo.AgentInfo.from_dict(raw_info) for (id, raw_info) in data['agent_infos'].items()},
            isolation_level = pacai.core.isolation.level.Level(data.get('isolation_level', pacai.core.isolation.level.Level.NONE.value)),
            max_turns = data.get('max_turns', DEFAULT_MAX_TURNS),
            agent_start_timeout = data.get('agent_start_timeout', DEFAULT_AGENT_START_TIMEOUT),
            agent_end_timeout = data.get('agent_end_timeout', DEFAULT_AGENT_END_TIMEOUT),
            agent_action_timeout = data.get('agent_action_timeout', DEFAULT_AGENT_ACTION_TIMEOUT),
            training = data.get('training', False),
            extra_info = data.get('extra_info', None))

class GameResult(edq.util.json.DictConverter):
    """ The result of running a game. """

    def __init__(self,
            game_id: int,
            game_info: GameInfo,
            score: float = 0,
            game_timeout: bool = False,
            timeout_agent_indexes: list[int] | None = None,
            crash_agent_indexes: list[int] | None = None,
            winning_agent_indexes: list[int] | None = None,
            start_time: edq.util.time.Timestamp | None = None,
            end_time: edq.util.time.Timestamp | None = None,
            history: list[pacai.core.agentaction.AgentActionRecord] | None = None,
            agent_complete_records: dict[int, pacai.core.agentaction.AgentActionRecord] | None = None,
            **kwargs: typing.Any) -> None:
        self.game_id: int = game_id
        """ The ID of the game result. """

        self.game_info: GameInfo = game_info
        """ The core information about this game. """

        if (start_time is None):
            start_time = edq.util.time.Timestamp.now()

        self.start_time: edq.util.time.Timestamp = start_time
        """ The time the game started at. """

        self.end_time: edq.util.time.Timestamp | None = end_time
        """ The time the game ended at. """

        if (history is None):
            history = []

        self.history: list[pacai.core.agentaction.AgentActionRecord] = history
        """ The history of actions taken by each agent in this game. """

        if (agent_complete_records is None):
            agent_complete_records = {}

        self.agent_complete_records: dict[int, pacai.core.agentaction.AgentActionRecord] = agent_complete_records
        """
        The record recieved from an agent when the game finishes.
        For agents that learn, this may include information that the agent learned this game.
        """

        self.score: float = score
        """ The score of the game. """

        self.game_timeout: bool = game_timeout
        """ Indicates that the game has timed out (reached the maximum number of moves). """

        if (timeout_agent_indexes is None):
            timeout_agent_indexes = []

        self.timeout_agent_indexes: list[int] = timeout_agent_indexes
        """ The list of agents that timed out in this game. """

        if (crash_agent_indexes is None):
            crash_agent_indexes = []

        self.crash_agent_indexes: list[int] = crash_agent_indexes
        """ The list of agents that crashed in this game. """

        if (winning_agent_indexes is None):
            winning_agent_indexes = []

        self.winning_agent_indexes: list[int] = winning_agent_indexes
        """
        The agents that are considered the "winner" of this game.
        Games may interpret this value in different ways.
        """

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'game_id': self.game_id,
            'game_info': self.game_info.to_dict(),
            'start_time': self.start_time,
            'end_time': self.end_time,
            'history': [item.to_dict() for item in self.history],
            'agent_complete_records': {agent_index: record.to_dict() for (agent_index, record) in self.agent_complete_records.items()},
            'score': self.score,
            'game_timeout': self.game_timeout,
            'timeout_agent_indexes': self.timeout_agent_indexes,
            'crash_agent_indexes': self.crash_agent_indexes,
            'winning_agent_indexes': self.winning_agent_indexes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        agent_complete_records = {}
        for (agent_index, raw_record) in data.get('agent_complete_records', {}).items():
            agent_complete_records[agent_index] = pacai.core.agentaction.AgentActionRecord.from_dict(raw_record)

        return cls(
            data['game_id'],
            GameInfo.from_dict(data['game_info']),
            start_time = data.get('start_time', None),
            end_time = data.get('end_time', None),
            history = [pacai.core.agentaction.AgentActionRecord.from_dict(item) for item in data.get('history', [])],
            agent_complete_records = agent_complete_records,
            score = data.get('score', 0),
            game_timeout = data.get('game_timeout', False),
            timeout_agent_indexes = data.get('timeout_agent_indexes', None),
            crash_agent_indexes = data.get('crash_agent_indexes', None),
            winning_agent_indexes = data.get('winning_agent_indexes', -1),
        )

    def get_duration_secs(self) -> float:
        """
        Get the game's duration in seconds.
        Will return positive infinity if the game has no end time
        (it is still going or crashed (in very rare cases)).
        """

        if (self.end_time is None):
            return math.inf

        return self.end_time.sub(self.start_time).to_secs()

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
        self.game_info: GameInfo = game_info
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

    def process_args(self, args: argparse.Namespace) -> None:
        """ Process any special arguments from the command-line. """

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
            result: GameResult,
            rng: random.Random,
            ) -> pacai.core.gamestate.GameState:
        """
        Process the given agent action and return an updated game state.
        The returned game state may be a copy or modified version of the passed in game state.
        """

        # The agent has timed out.
        if (action_record.timeout):
            result.timeout_agent_indexes.append(action_record.agent_index)
            state.process_agent_timeout(action_record.agent_index)
            return state

        # The agent has crashed.
        if (action_record.crashed):
            result.crash_agent_indexes.append(action_record.agent_index)
            state.process_agent_crash(action_record.agent_index)
            return state

        action = action_record.get_action()
        if (action not in state.get_legal_actions()):
            raise ValueError(f"Illegal action for agent {action_record.agent_index}: '{action}'.")

        self._call_state_process_turn_full(state, action, rng)

        return state

    def _call_state_process_turn_full(self,
            state: pacai.core.gamestate.GameState,
            action: pacai.core.action.Action,
            rng: random.Random) -> None:
        """ Call on the game state to process a full turn. """

        state.process_turn_full(action, rng)

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

        logging.debug("Starting a game with seed: %d.", self.game_info.seed)

        # Create a new random number generator just for this game.
        rng = random.Random(self.game_info.seed)

        # Keep track of what happens during this game.
        game_id = rng.randint(0, 2**64)
        result = GameResult(game_id, self.game_info)

        # Initialize the agent isolator.
        isolator = self.game_info.isolation_level.get_isolator()
        isolator.init_agents(self.game_info.agent_infos)

        # Keep track of all the user inputs since the last time an agent moved.
        # Note that we need to keep track for all agents,
        # since the UI will only tell us the inputs since the last call.
        agent_user_inputs: dict[int, list[pacai.core.action.Action]] = {}
        for agent_index in self.game_info.agent_infos:
            agent_user_inputs[agent_index] = []

        # Create the initial game state (and force it's seed).
        state = self.get_initial_state(rng, self._board, self.game_info.agent_infos)
        state.seed = game_id
        state.game_start()

        board_highlights: list[pacai.core.board.Highlight] = []

        # Notify agents about the start of the game.
        records = isolator.game_start(rng, state, self.game_info.agent_start_timeout)
        for record in records.values():
            if (record.timeout):
                result.timeout_agent_indexes.append(record.agent_index)
                state.process_agent_timeout(record.agent_index)
            elif (record.crashed):
                result.crash_agent_indexes.append(record.agent_index)
                state.process_agent_crash(record.agent_index)
            else:
                board_highlights += record.get_board_highlights()

        state.agents_game_start(records)

        # Start the UI.
        ui.game_start(state, board_highlights = board_highlights)

        while (not self.check_end(state)):
            logging.trace("Turn %d, agent %d.", state.turn_count, state.agent_index)  # type: ignore[attr-defined]  # pylint: disable=no-member

            # Receive any user inputs from the UI.
            self._receive_user_inputs(agent_user_inputs, ui)

            # Get the next action from the agent.
            action_record = isolator.get_action(state, agent_user_inputs[state.agent_index], self.game_info.agent_action_timeout)

            # Check if we need to clear any user inputs.
            if (action_record.get_clear_inputs()):
                agent_user_inputs[state.agent_index] = []

            # Execute the next action and update the state.
            state = self.process_turn(state, action_record, result, rng)

            # Update the UI.
            ui.update(state, board_highlights = action_record.get_board_highlights())

            # Update the game result and move history.
            result.history.append(action_record)

            # Check for game ending conditions.
            if (self.check_end(state)):
                break

            # Check if this game has ran for the maximum number of turns.
            if ((self.game_info.max_turns > 0) and (state.turn_count >= self.game_info.max_turns)):
                state.process_game_timeout()
                result.game_timeout = True
                break

        # Mark the end time of the game.
        result.end_time = edq.util.time.Timestamp.now()

        # Notify the state about the end of the game.
        winners = state.game_complete()
        result.winning_agent_indexes += winners

        result.score = state.score

        # Notify agents about the end of this game.
        result.agent_complete_records = isolator.game_complete(state, self.game_info.agent_end_timeout)

        # All the game to make final updates to the result.
        self.game_complete(state, result)

        # Update the UI.
        ui.game_complete(state)

        # Cleanup
        isolator.close()
        ui.close()

        if ((not self._is_replay) and (self._save_path is not None)):
            logging.info("Saving results to '%s'.", self._save_path)
            edq.util.json.dump_path(result, self._save_path)

        return result

    def _receive_user_inputs(self,
            agent_user_inputs: dict[int, list[pacai.core.action.Action]],
            ui: pacai.core.ui.UI,
            ) -> None:
        """ Add the current user inputs to the running list for each agent. """

        new_user_inputs = ui.get_user_inputs()

        for user_inputs in agent_user_inputs.values():
            user_inputs += new_user_inputs

    @classmethod
    def override_args_with_replay(cls,
            args: argparse.Namespace, base_agent_infos: dict[int, pacai.core.agentinfo.AgentInfo]) -> None:
        """
        Override the args with the settings from the replay in the args.
        Children may extend this for additional functionality.
        """

        logging.info("Loading replay from '%s'.", args.replay_path)
        replay_info = typing.cast(GameResult, edq.util.json.load_object_path(args.replay_path, GameResult))

        # Overrides from the replay info.
        args.board = replay_info.game_info.board_source
        args.seed = replay_info.game_info.seed

        # Special settings for replays.
        args.num_games = 1
        args.num_training = 0
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
                name = pacai.util.alias.AGENT_SCRIPTED.short,
                move_delay = replay_info.game_info.agent_infos[agent_index].move_delay,
                actions = actions,
            )

def set_cli_args(parser: argparse.ArgumentParser, default_board: str | None = None) -> argparse.ArgumentParser:
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

    parser.add_argument('--num-training', dest = 'num_training',
            action = 'store', type = int, default = 0,
            help = 'The number of games to play in training mode before playing `--num-games` real games (default: %(default)s).')

    parser.add_argument('--seed', dest = 'seed',
            action = 'store', type = int, default = None,
            help = 'The random seed for the game (will be randomly generated if not set.')

    parser.add_argument('--max-turns', dest = 'max_turns',
            action = 'store', type = int, default = DEFAULT_MAX_TURNS,
            help = 'The maximum number of turns/moves (total for all agents) allowed in this game (-1 for unlimited) (default: %(default)s).')

    parser.add_argument('--agent-start-timeout', dest = 'agent_start_timeout',
            action = 'store', type = float, default = DEFAULT_AGENT_START_TIMEOUT,
            help = ('The maximum number of seconds each agent is allowed when starting a game (<= 0 for unlimited time) (default: %(default)s).'
                    + ' Note that the "none" isolation level cannot enforce timeouts.'))

    parser.add_argument('--agent-end-timeout', dest = 'agent_end_timeout',
            action = 'store', type = float, default = DEFAULT_AGENT_END_TIMEOUT,
            help = ('The maximum number of seconds each agent is allowed when ending a game (<= 0 for unlimited time) (default: %(default)s).'
                    + ' Note that the "none" isolation level cannot enforce timeouts.'))

    parser.add_argument('--agent-action-timeout', dest = 'agent_action_timeout',
            action = 'store', type = float, default = DEFAULT_AGENT_ACTION_TIMEOUT,
            help = ('The maximum number of seconds each agent is allowed when getting an action (<= 0 for unlimited time) (default: %(default)s).'
                    + ' Note that the "none" isolation level cannot enforce timeouts.'))

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

    return parser

def init_from_args(
        args: argparse.Namespace,
        game_class: typing.Type[Game],
        base_agent_infos: dict[int, pacai.core.agentinfo.AgentInfo] | None = None,
        remove_agent_indexes: list[int] | None = None,
        board_options: dict[str, typing.Any] | None = None,
        ) -> argparse.Namespace:
    """
    Take in args from a parser that was passed to set_cli_args(),
    and initialize the proper components.
    This will create a number of games (and related resources)
    based on `--num-games` + `--num-training`.
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
        game_class.override_args_with_replay(args, base_agent_infos)
        remove_agent_indexes = []

    if (args.board is None):
        raise ValueError("No board was specified.")

    total_games = args.num_games + args.num_training

    if (total_games <= 0):
        raise ValueError(f"At least one game must be played (--num-games + --num-training), {total_games} was specified.")

    # Establish an RNG to generate seeds for each game using the given seed.
    seed = args.seed
    if (seed is None):
        seed = random.randint(0, 2**64)

    logging.debug("Using source seed for games: %d.", seed)
    rng = random.Random(seed)

    if (board_options is None):
        board_options = {}

    # Either take the board as given, or load it from a path.
    if (isinstance(args.board, pacai.core.board.Board)):
        board = args.board
    else:
        board = pacai.core.board.load_path(args.board, **board_options)

    # Remove specified agents from the board.
    remove_agent_indexes += args.remove_agent_indexes
    for remove_agent_index in remove_agent_indexes:
        board.remove_agent(remove_agent_index)

    agent_infos = _parse_agent_infos(board.agent_indexes(), args.raw_agent_args, base_agent_infos, remove_agent_indexes)

    base_save_path = args.save_path

    all_boards = []
    all_agent_infos = []
    all_games = []

    for i in range(total_games):
        game_seed = rng.randint(0, 2**64)

        all_boards.append(board.copy())
        all_agent_infos.append(copy.deepcopy(agent_infos))

        game_info = GameInfo(
                board.source,
                all_agent_infos[-1],
                isolation_level = pacai.core.isolation.level.Level(args.isolation_level),
                max_turns = args.max_turns,
                agent_start_timeout = args.agent_start_timeout,
                agent_end_timeout = args.agent_end_timeout,
                agent_action_timeout = args.agent_action_timeout,
                training = (i < args.num_training),
                seed = game_seed
        )

        # Suffix the save path if there is more than one game.
        save_path = base_save_path
        if ((save_path is not None) and (total_games > 1)):
            parts = os.path.splitext(save_path)
            save_path = f"{parts[0]}_{i:03d}{parts[1]}"

        game_args = {
            'game_info': game_info,
            'board': all_boards[-1],
            'save_path': save_path,
        }

        game = game_class(**game_args)
        game.process_args(args)

        all_games.append(game)

    setattr(args, '_boards', all_boards)
    setattr(args, '_agent_infos', all_agent_infos)
    setattr(args, '_games', all_games)

    return args

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

        agent_info[agent_index].set_from_string(key, value)

    # Remove specified agents.
    for remove_agent_index in remove_agent_indexes:
        if (remove_agent_index in agent_info):
            del agent_info[remove_agent_index]

    return agent_info
