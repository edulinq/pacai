import argparse
import logging
import typing

import pacai.core.agentaction
import pacai.core.agentinfo
import pacai.core.board
import pacai.core.game
import pacai.core.log
import pacai.core.ui
import pacai.util.alias

SCORE_LIST_MAX_INFO_LENGTH: int = 50
""" If a score list is less than this, log it to info. """

@typing.runtime_checkable
class SetCLIArgs(typing.Protocol):
    """
    A function that can be used to modify a CLI parser before use.
    """

    def __call__(self,
            parser: argparse.ArgumentParser,
            ) -> argparse.ArgumentParser:
        """
        Modify the CLI parser before use.
        Any changes may be made, including adding arguments.
        The modified (or new) parser should be returned.
        """

@typing.runtime_checkable
class GetAdditionalOptions(typing.Protocol):
    """
    A function that can be used to get additional initialization options.
    """

    def __call__(self,
            args: argparse.Namespace,
            ) -> dict[str, typing.Any]:
        """
        Get additional/custom initialization options.
        """

@typing.runtime_checkable
class InitFromArgs(typing.Protocol):
    """
    A function that can be used to initialize components from CLI args.
    """

    def __call__(self,
            args: argparse.Namespace,
            ) -> tuple[dict[int, pacai.core.agentinfo.AgentInfo], list[int], dict[str, typing.Any]]:
        """
        Initialize components from arguments and return
        the base agent infos, a list of agents to remove from the board, as well as any board options.
        See base_init_from_args() for the default implementation.
        """

@typing.runtime_checkable
class LogResults(typing.Protocol):
    """
    A function that can be used to log game results.
    """

    def __call__(self,
            results: list[pacai.core.game.GameResult],
            winning_agent_indexes: set[int],
            prefix: str = '',
            ) -> None:
        """
        Log the result of running several games.
        """

def base_init_from_args(args: argparse.Namespace) -> tuple[dict[int, pacai.core.agentinfo.AgentInfo], list[int], dict[str, typing.Any]]:
    """
    Take in args from a parser that was passed to set_cli_args(),
    and initialize the proper components.
    """

    base_agent_infos: dict[int, pacai.core.agentinfo.AgentInfo] = {}

    # Create base arguments for all possible agents.
    for i in range(pacai.core.board.MAX_AGENTS):
        base_agent_infos[i] = pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_RANDOM.long)

    return base_agent_infos, [], {}

def base_log_results(results: list[pacai.core.game.GameResult], winning_agent_indexes: set[int], prefix: str = '') -> None:
    """
    Log the result of running several games.
    """

    scores = [result.score for result in results]
    wins = [(not winning_agent_indexes.isdisjoint(set(result.winning_agent_indexes))) for result in results]
    win_rate = wins.count(True) / float(len(wins))
    turn_counts = [len(result.history) for result in results]

    # Avoid logging long lists (which can be a bit slow in Python's logging module).
    log_lists_to_info = (len(results) < SCORE_LIST_MAX_INFO_LENGTH)
    log_lists_to_debug = (logging.getLogger().getEffectiveLevel() <= logging.DEBUG)

    joined_scores = ''
    joined_record = ''
    joined_turn_counts = ''

    if (log_lists_to_info or log_lists_to_debug):
        joined_scores = ', '.join([str(score) for score in scores])
        joined_record = ', '.join([['Loss', 'Win'][int(win)] for win in wins])
        joined_turn_counts = ', '.join([str(turn_count) for turn_count in turn_counts])

    logging.info('%sAverage Score: %s', prefix, sum(scores) / float(len(results)))

    if (log_lists_to_info):
        logging.info('%sScores:        %s', prefix, joined_scores)
    elif (log_lists_to_debug):
        logging.debug('%sScores:        %s', prefix, joined_scores)

    logging.info('%sWin Rate:      %d / %d (%0.2f)', prefix, wins.count(True), len(wins), win_rate)

    if (log_lists_to_info):
        logging.info('%sRecord:        %s', prefix, joined_record)
    elif (log_lists_to_debug):
        logging.debug('%sRecord:        %s', prefix, joined_record)

    logging.info('%sAverage Turns: %s', prefix, sum(turn_counts) / float(len(results)))

    if (log_lists_to_info):
        logging.info('%sTurn Counts:   %s', prefix, joined_turn_counts)
    elif (log_lists_to_debug):
        logging.debug('%sTurn Counts:   %s', prefix, joined_turn_counts)

def run_main(
        description: str,
        default_board: str,
        game_class: typing.Type[pacai.core.game.Game],
        custom_set_cli_args: SetCLIArgs | None = None,
        get_additional_ui_options: GetAdditionalOptions | None = None,
        custom_init_from_args: InitFromArgs = base_init_from_args,
        winning_agent_indexes: set[int] | None = None,
        log_results: LogResults | None = base_log_results,
        argv: list[str] | None = None,
        ) -> tuple[list[pacai.core.game.GameResult], list[pacai.core.game.GameResult]]:
    """
    A full main function to prep and run games.

    Will return the results of any training games followed by the results of any non-training games.
    """

    # Create a CLI parser.
    parser = get_parser(description, default_board, custom_set_cli_args = custom_set_cli_args)

    # Parse the CLI args.
    args = parse_args(parser, game_class,
            get_additional_ui_options = get_additional_ui_options, custom_init_from_args = custom_init_from_args,
            argv = argv)

    return run_games(args, winning_agent_indexes = winning_agent_indexes, log_results = log_results)

def get_parser(
        description: str,
        default_board: str,
        custom_set_cli_args: SetCLIArgs | None = None,
        ) -> argparse.ArgumentParser:
    """ Get a parser with all the options. """

    parser = argparse.ArgumentParser(description = description)

    # Add logging arguments.
    parser = pacai.core.log.set_cli_args(parser)

    # Add UI arguments.
    parser = pacai.core.ui.set_cli_args(parser)

    # Add game arguments.
    parser = pacai.core.game.set_cli_args(parser, default_board = default_board)

    # Add custom options.
    if (custom_set_cli_args is not None):
        parser = custom_set_cli_args(parser)

    return parser

def parse_args(
        parser: argparse.ArgumentParser,
        game_class: typing.Type[pacai.core.game.Game],
        get_additional_ui_options: GetAdditionalOptions | None = None,
        custom_init_from_args: InitFromArgs = base_init_from_args,
        argv: list[str] | None = None,
        ) -> argparse.Namespace:
    """ Parse the args from the parser returned by get_parser(). """

    args = parser.parse_args(args = argv)

    # Parse logging arguments.
    args = pacai.core.log.init_from_args(parser, args)

    # Parse custom options.
    base_agent_infos, remove_agent_indexes, board_options = custom_init_from_args(args)

    # Parse UI arguments.

    additional_ui_args = {}
    if (get_additional_ui_options is not None):
        additional_ui_args = get_additional_ui_options(args)

    null_out_uis = args.num_training
    if (args.show_training_ui):
        null_out_uis = 0

    args = pacai.core.ui.init_from_args(args, null_out_uis = null_out_uis, additional_args = additional_ui_args)

    # Parse game arguments.

    args = pacai.core.game.init_from_args(args, game_class,
            base_agent_infos = base_agent_infos,
            remove_agent_indexes = remove_agent_indexes,
            board_options = board_options)

    return args

def run_games(
        args: argparse.Namespace,
        winning_agent_indexes: set[int] | None = None,
        log_results: LogResults | None = base_log_results,
        ) -> tuple[list[pacai.core.game.GameResult], list[pacai.core.game.GameResult]]:
    """
    Run one or more standard games using pre-parsed arguments.
    The arguments are expected to have `_games` and `_uis`,
    as if `pacai.core.ui.init_from_args()` and `pacai.core.game.init_from_args()` have been called.

    Will return the results of any training games followed by the results of any non-training games.
    """

    if (winning_agent_indexes is None):
        winning_agent_indexes = set()

    training_infos: dict[int, dict[str, typing.Any]] = {}
    training_results = []

    # Run training games/epochs.
    for i in range(args.num_training):
        game = args._games[i]
        ui = args._uis[i]

        for (agent_index, agent_info) in game.game_info.agent_infos.items():
            # Set information gained from the previous training epochs.
            data = training_infos.get(agent_index, {}).copy()

            # Tell agents we are training.
            data['training'] = True
            data['training_epoch'] = i

            agent_info.extra_arguments.update(data)

        result = game.run(ui)
        training_results.append(result)

        for (agent_index, agent_record) in result.agent_complete_records.items():
            if (agent_record.agent_action is not None):
                training_infos[agent_index] = agent_record.agent_action.training_info

    results = []

    for i in range(args.num_games):
        game = args._games[i + args.num_training]
        ui = args._uis[i + args.num_training]

        # Set any information gained from training.
        for (agent_index, training_info) in training_infos.items():
            game.game_info.agent_infos[agent_index].extra_arguments.update(training_info)

        result = game.run(ui)
        results.append(result)

    if (len(training_results) > 0):
        if (log_results is not None):
            log_results(training_results, winning_agent_indexes, prefix = 'Training ')

    if (len(results) > 0):
        if (log_results is not None):
            log_results(results, winning_agent_indexes)

    return training_results, results
