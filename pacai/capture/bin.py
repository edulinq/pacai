"""
The main executable for running a game of Capture.
"""

import argparse
import logging
import typing

import pacai.capture.board
import pacai.capture.game
import pacai.capture.team
import pacai.util.alias
import pacai.util.bin

DEFAULT_BOARD: str = 'capture-medium'
DEFAULT_SPRITE_SHEET: str = 'capture'

def set_cli_args(parser: argparse.ArgumentParser, **kwargs: typing.Any) -> argparse.ArgumentParser:
    """
    Set Capture-specific CLI arguments.
    This is a sibling to init_from_args(), as the arguments set here can be interpreted there.
    """

    parser.add_argument('--red-team', dest = 'red_team_func', metavar = 'TEAM_CREATION_FUNC',
            action = 'store', type = str, default = pacai.util.alias.CAPTURE_TEAM_DUMMY.short,
            help = ('Select the capture team that will play on the red team (default: %(default)s).'
                    + f' Builtin teams: {pacai.util.alias.CAPTURE_TEAM_SHORT_NAMES}.'))

    parser.add_argument('--blue-team', dest = 'blue_team_func', metavar = 'TEAM_CREATION_FUNC',
            action = 'store', type = str, default = pacai.util.alias.CAPTURE_TEAM_DUMMY.short,
            help = ('Select the capture team that will play on the blue team (default: %(default)s).'
                    + f' Builtin teams: {pacai.util.alias.CAPTURE_TEAM_SHORT_NAMES}.'))

    # Edit the --board argument to add informastion about random boards.
    board_arg = getattr(parser, '_option_string_actions', {}).get('--board', None)
    if (board_arg is not None):
        board_arg.help = board_arg.help.replace(', or just a filename', ', just a filename, or `random[-seed]` (e.g. "random", "random-123")')

    return parser

def init_from_args(args: argparse.Namespace) -> tuple[dict[int, pacai.core.agentinfo.AgentInfo], list[int], dict[str, typing.Any]]:
    """
    Setup agents based on Capture rules.

    Agent infos are supplied via the --red-team and --blue-team arguments.
    The board dictates how many agents will be used.
    Extra agents will be ignored, and missing agents will be filled in with random agents.
    """

    red_team_func = pacai.util.reflection.resolve_and_fetch(pacai.capture.team.TeamCreationFunction, args.red_team_func)
    blue_team_func = pacai.util.reflection.resolve_and_fetch(pacai.capture.team.TeamCreationFunction, args.blue_team_func)

    red_team_base = red_team_func()
    blue_team_base = blue_team_func()

    base_agent_infos: dict[int, pacai.core.agentinfo.AgentInfo] = {}
    for i in range(pacai.core.board.MAX_AGENTS):
        agent_info = pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_RANDOM.long)

        team_base = red_team_base
        if (i % 2 == 1):
            team_base = blue_team_base

        if (len(team_base) > 0):
            agent_info = team_base.pop(0)

        base_agent_infos[i] = agent_info

    # Check for random boards.
    args.board = pacai.capture.game.Game.check_for_random_board(args.board)

    return base_agent_infos, [], {}

def get_additional_ui_options(args: argparse.Namespace) -> dict[str, typing.Any]:
    """ Get additional options for the UI. """

    return {
        'sprite_sheet_path': DEFAULT_SPRITE_SHEET,
    }

def log_capture_results(results: list[pacai.core.game.GameResult], winning_agent_indexes: set[int], prefix: str = '') -> None:
    """
    Log the result of running several games.
    """

    scores = [result.score for result in results]
    turn_counts = [len(result.history) for result in results]

    record = [('red' if (score < 0.0) else 'blue' if (score > 0.0) else 'tie') for score in scores]

    # Avoid logging long lists (which can be a bit slow in Python's logging module).
    log_lists_to_info = (len(results) < pacai.util.bin.SCORE_LIST_MAX_INFO_LENGTH)
    log_lists_to_debug = (logging.getLogger().getEffectiveLevel() <= logging.DEBUG)

    joined_scores = ''
    joined_record = ''
    joined_turn_counts = ''

    if (log_lists_to_info or log_lists_to_debug):
        joined_scores = ', '.join([str(score) for score in scores])
        joined_record = ', '.join(record)
        joined_turn_counts = ', '.join([str(turn_count) for turn_count in turn_counts])

    logging.info('%sAverage Score: %s', prefix, sum(scores) / float(len(results)))

    if (log_lists_to_info):
        logging.info('%sScores:        %s', prefix, joined_scores)
    elif (log_lists_to_debug):
        logging.debug('%sScores:        %s', prefix, joined_scores)

    if (log_lists_to_info):
        logging.info('%sRecord:        %s', prefix, joined_record)
    elif (log_lists_to_debug):
        logging.debug('%sRecord:        %s', prefix, joined_record)

    logging.info('%sAverage Turns: %s', prefix, sum(turn_counts) / float(len(results)))

    if (log_lists_to_info):
        logging.info('%sTurn Counts:   %s', prefix, joined_turn_counts)
    elif (log_lists_to_debug):
        logging.debug('%sTurn Counts:   %s', prefix, joined_turn_counts)

def main(argv: list[str] | None = None,
        ) -> tuple[list[pacai.core.game.GameResult], list[pacai.core.game.GameResult]]:
    """
    Invoke a game of Capture.

    Will return the results of any training games followed by the results of any non-training games.
    """

    return pacai.util.bin.run_main(
        description = "Play a game of Capture.",
        default_board = DEFAULT_BOARD,
        game_class = pacai.capture.game.Game,
        get_additional_ui_options = get_additional_ui_options,
        custom_set_cli_args = set_cli_args,
        custom_init_from_args = init_from_args,
        log_results = log_capture_results,
        argv = argv,
    )

if (__name__ == '__main__'):
    main()
