"""
The main executable for running a game of Pac-Man.
"""

import argparse
import sys

import pacai.core.agentinfo
import pacai.core.board
import pacai.core.log
import pacai.core.ui
import pacai.pacman.game
import pacai.pacman.gamestate
import pacai.util.bin
import pacai.util.alias

DEFAULT_BOARD: str = 'classic-medium'
DEFAULT_SPRITE_SHEET: str = 'pacman'

def run(args: argparse.Namespace) -> int:
    """ Run one or more gaames of Pac-Man using pre-parsed arguments. """

    return pacai.util.bin.run_games(args, {pacai.pacman.gamestate.PACMAN_AGENT_INDEX})

def set_cli_args(parser: argparse.ArgumentParser) -> None:
    """
    Set Pac-Man-specific CLI arguments.
    This is a sibling to init_from_args(), as the arguments set here can be interpreted there.
    """

    parser.add_argument('--pacman', dest = 'pacman', metavar = 'AGENT_TYPE',
            action = 'store', type = str, default = pacai.util.alias.AGENT_USER_INPUT.short,
            help = ('Select the agent type that PacMan will use (default: %(default)s).'
                    + f' Builtin agents: {pacai.util.alias.AGENT_SHORT_NAMES}.'))

    parser.add_argument('--ghosts', dest = 'ghosts', metavar = 'AGENT_TYPE',
            action = 'store', type = str, default = pacai.util.alias.AGENT_RANDOM.short,
            help = ('Select the agent type that all ghosts will use (default: %(default)s).'
                    + f' Builtin agents: {pacai.util.alias.AGENT_SHORT_NAMES}.'))

    parser.add_argument('--num-ghosts', dest = 'num_ghosts',
            action = 'store', type = int, default = -1,
            help = ('The maximum number of ghosts on the board (default: %(default)s).'
                    + ' Ghosts with the highest agent index will be removed first.'
                    + ' Board positions that normally spawn the removed agents/ghosts will now be empty.'))

def init_from_args(args: argparse.Namespace) -> tuple[dict[int, pacai.core.agentinfo.AgentInfo], list[int]]:
    """
    Take in args from a parser that was passed to set_cli_args(),
    and initialize the proper components.
    """

    base_agent_infos: dict[int, pacai.core.agentinfo.AgentInfo] = {}

    # Create base arguments for all possible agents.
    for i in range(pacai.core.board.MAX_AGENTS):
        if (i == 0):
            base_agent_infos[i] = pacai.core.agentinfo.AgentInfo(name = args.pacman)
        else:
            base_agent_infos[i] = pacai.core.agentinfo.AgentInfo(name = args.ghosts)

    remove_agent_indexes = []

    if (args.num_ghosts >= 0):
        for i in range(1 + args.num_ghosts, pacai.core.board.MAX_AGENTS):
            remove_agent_indexes.append(i)

    return base_agent_infos, remove_agent_indexes

def _parse_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    """ Parse the args from the parser returned by _get_parser(). """

    args = parser.parse_args()

    # Parse logging arguments.
    args = pacai.core.log.init_from_args(args)

    # Parse ui arguments.
    additional_ui_args = {
        'sprite_sheet_path': DEFAULT_SPRITE_SHEET,
    }
    args = pacai.core.ui.init_from_args(args, additional_args = additional_ui_args)

    # Parse Pac-Man-specific options.
    base_agent_infos, remove_agent_indexes = init_from_args(args)

    # Parse game arguments.
    args = pacai.core.game.init_from_args(args, pacai.pacman.game.Game,
            base_agent_infos = base_agent_infos, remove_agent_indexes = remove_agent_indexes)

    return args

def _get_parser() -> argparse.ArgumentParser:
    """ Get a parser with all the options set to handle Pac-Man. """

    parser = argparse.ArgumentParser(description = "Play a game of Pac-Man.")

    # Add logging arguments.
    pacai.core.log.set_cli_args(parser)

    # Add UI arguments.
    pacai.core.ui.set_cli_args(parser)

    # Add game arguments.
    pacai.core.game.set_cli_args(parser, default_board = DEFAULT_BOARD)

    # Add Pac-Man-specific options.
    set_cli_args(parser)

    return parser

def main() -> int:
    """ Invoke a game of Pac-Man. """

    args = _parse_args(_get_parser())
    return run(args)

if (__name__ == '__main__'):
    sys.exit(main())
