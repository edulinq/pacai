"""
The main executable for running a game of Pac-Man.
"""

import argparse
import sys

import pacai.core.agent
import pacai.core.board
import pacai.core.log
import pacai.core.ui
import pacai.pacman.game

DEFAULT_BOARD: str = 'medium-classic'
DEFAULT_SPRITE_SHEET: str = 'pacman'

def run(args: argparse.Namespace) -> int:
    args._game.run(args._ui)
    return 0

def set_cli_args(parser: argparse.ArgumentParser) -> None:
    """
    Set pacman-specific CLI arguments.
    This is a sibling to init_from_args(), as the arguments set here can be interpreted there.
    """

    parser.add_argument('--pacman', dest = 'pacman', metavar  = 'AGENT_TYPE',
            action = 'store', type = str, default = 'pacai.agents.userinput.UserInputAgent',
            help = 'Select the agent type that PacMan will use (default: %(default)s).')

    parser.add_argument('--ghosts', dest = 'ghosts', metavar  = 'AGENT_TYPE',
            action = 'store', type = str, default = 'pacai.agents.random.RandomAgent',
            help = 'Select the agent type that all ghosts will use (default: %(default)s).')

    parser.add_argument('--num-ghosts', dest = 'num_ghosts',
            action = 'store', type = int, default = -1,
            help = ('The maximum number of ghosts on the board (default: %(default)s).'
                    + ' Ghosts with the highest agent index will be removed first.'
                    + ' Board positions that normally spawn the removed agents/ghosts will now be empty.'))

def init_from_args(args: argparse.Namespace) -> tuple[dict[int, pacai.core.agent.AgentArguments], list[int]]:
    """
    Take in args from a parser that was passed to set_cli_args(),
    and initialize the proper components.
    """

    base_agent_args: dict[int, pacai.core.agent.AgentArguments] = {}

    # Create base arguments for all possible agents.
    for i in range(pacai.core.board.MAX_AGENTS):
        if (i == 0):
            base_agent_args[i] = pacai.core.agent.AgentArguments(name = args.pacman)
        else:
            base_agent_args[i] = pacai.core.agent.AgentArguments(name = args.ghosts)

    remove_agent_indexes = []

    if (args.num_ghosts >= 0):
        for i in range(1 + args.num_ghosts, pacai.core.board.MAX_AGENTS):
            remove_agent_indexes.append(i)

    return base_agent_args, remove_agent_indexes


def _parse_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    args = parser.parse_args()

    # Parse logging arguments.
    args = pacai.core.log.init_from_args(args)

    # Parse pacman-specific options.
    base_agent_args, remove_agent_indexes = init_from_args(args)

    # Parse game arguments.
    args = pacai.core.game.init_from_args(args, pacai.pacman.game.Game, base_agent_args = base_agent_args, remove_agent_indexes = remove_agent_indexes)

    # Parse ui arguments.
    additional_ui_args = {
        'sprite_sheet_path': DEFAULT_SPRITE_SHEET,
    }
    args = pacai.core.ui.init_from_args(args, additional_args = additional_ui_args)

    return args

def _get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description = "Play a game of Pac-Man.")

    # Add logging arguments.
    pacai.core.log.set_cli_args(parser)

    # Add game arguments.
    pacai.core.game.set_cli_args(parser, default_board = DEFAULT_BOARD)

    # Add UI arguments.
    pacai.core.ui.set_cli_args(parser)

    # Add pacman-specific options.
    set_cli_args(parser)

    return parser

def main() -> int:
    args = _parse_args(_get_parser())
    return run(args)

if (__name__ == '__main__'):
    sys.exit(main())
