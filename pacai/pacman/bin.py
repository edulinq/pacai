"""
The main executable for running a game of Pac-Man.
"""

import argparse
import typing

import pacai.core.agentinfo
import pacai.core.board
import pacai.pacman.game
import pacai.pacman.gamestate
import pacai.util.bin
import pacai.util.alias

DEFAULT_BOARD: str = 'classic-medium'
DEFAULT_SPRITE_SHEET: str = 'pacman'

def set_cli_args(parser: argparse.ArgumentParser, **kwargs: typing.Any) -> argparse.ArgumentParser:
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

    return parser

def init_from_args(args: argparse.Namespace) -> tuple[dict[int, pacai.core.agentinfo.AgentInfo], list[int], dict[str, typing.Any]]:
    """
    Setup agents based on Pac-Man rules.
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

    return base_agent_infos, remove_agent_indexes, {}

def get_additional_ui_options(args: argparse.Namespace) -> dict[str, typing.Any]:
    """ Get additional options for the UI. """

    return {
        'sprite_sheet_path': DEFAULT_SPRITE_SHEET,
    }

def main(argv: list[str] | None = None,
        ) -> tuple[list[pacai.core.game.GameResult], list[pacai.core.game.GameResult]]:
    """
    Invoke a game of Pac-Man.

    Will return the results of any training games followed by the results of any non-training games.
    """

    return pacai.util.bin.run_main(
        description = "Play a game of Pac-Man.",
        default_board = DEFAULT_BOARD,
        game_class = pacai.pacman.game.Game,
        get_additional_ui_options = get_additional_ui_options,
        custom_set_cli_args = set_cli_args,
        custom_init_from_args = init_from_args,
        winning_agent_indexes = {pacai.pacman.gamestate.PACMAN_AGENT_INDEX},
        argv = argv,
    )

if (__name__ == '__main__'):
    main()
