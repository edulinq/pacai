"""
The main executable for running a game of Capture.
"""

import argparse
import sys
import typing

import pacai.capture.board
import pacai.capture.game
import pacai.capture.team
import pacai.util.alias
import pacai.util.bin

DEFAULT_BOARD: str = 'capture-medium'
DEFAULT_SPRITE_SHEET: str = 'capture'

RANDOM_BOARD_PREFIX: str = 'random'

def set_cli_args(parser: argparse.ArgumentParser, **kwargs) -> argparse.ArgumentParser:
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
    if (args.board.startswith(RANDOM_BOARD_PREFIX)):
        board_seed = None
        if (args.board != RANDOM_BOARD_PREFIX):
            # Strip 'random-' and 'random'.
            board_seed = int(args.board.removeprefix(RANDOM_BOARD_PREFIX + '-').removeprefix(RANDOM_BOARD_PREFIX))

        args.board = pacai.capture.board.generate(seed = board_seed)

    return base_agent_infos, [], {}

def get_additional_ui_options(args: argparse.Namespace) -> dict[str, typing.Any]:
    """ Get additional options for the UI. """

    return {
        'sprite_sheet_path': DEFAULT_SPRITE_SHEET,
    }

def main() -> int:
    """ Invoke a game of Capture. """

    return pacai.util.bin.run_main(
        description = "Play a game of Capture.",
        default_board = DEFAULT_BOARD,
        game_class = pacai.capture.game.Game,
        get_additional_ui_options = get_additional_ui_options,
        custom_set_cli_args = set_cli_args,
        custom_init_from_args = init_from_args,
    )

if (__name__ == '__main__'):
    sys.exit(main())
