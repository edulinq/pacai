"""
The main executable for running a game of Capture.
"""

import argparse
import sys
import typing

import pacai.capture.game
import pacai.core.agentinfo
import pacai.core.board
import pacai.util.bin
import pacai.util.alias

DEFAULT_BOARD: str = 'classic-medium'
DEFAULT_SPRITE_SHEET: str = 'pacman'

def set_cli_args(parser: argparse.ArgumentParser, **kwargs) -> argparse.ArgumentParser:
    """
    Set Capture-specific CLI arguments.
    This is a sibling to init_from_args(), as the arguments set here can be interpreted there.
    """

    # TEST
    parser.add_argument('--pacman', dest = 'pacman', metavar = 'AGENT_TYPE',
            action = 'store', type = str, default = pacai.util.alias.AGENT_USER_INPUT.short,
            help = ('Select the agent type that PacMan will use (default: %(default)s).'
                    + f' Builtin agents: {pacai.util.alias.AGENT_SHORT_NAMES}.'))

    return parser

def init_from_args(args: argparse.Namespace) -> tuple[dict[int, pacai.core.agentinfo.AgentInfo], list[int], dict[str, typing.Any]]:
    """
    Setup agents based on Capture rules.
    """

    base_agent_infos: dict[int, pacai.core.agentinfo.AgentInfo] = {}

    # TEST

    # Create base arguments for all possible agents.
    for i in range(pacai.core.board.MAX_AGENTS):
        if (i == 0):
            base_agent_infos[i] = pacai.core.agentinfo.AgentInfo(name = args.pacman)
        else:
            base_agent_infos[i] = pacai.core.agentinfo.AgentInfo(name = args.ghosts)

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
        custom_set_cli_args = set_cli_args,
        get_additional_ui_options = get_additional_ui_options,
        custom_init_from_args = init_from_args,
    )

if (__name__ == '__main__'):
    sys.exit(main())
