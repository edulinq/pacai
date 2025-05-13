"""
The main executable for running a game of Pac-Man.
"""

import argparse
import logging
import sys
import typing

import PIL.Image

import pacai.core.agentinfo
import pacai.core.board
import pacai.core.gamestate
import pacai.core.log
import pacai.core.spritesheet
import pacai.core.ui
import pacai.pacman.game
import pacai.pacman.gamestate
import pacai.util.alias

DEFAULT_BOARD: str = 'classic-medium'
DEFAULT_SPRITE_SHEET: str = 'pacman'

SCARED_GHOST_MARKER: pacai.core.board.Marker = pacai.core.board.Marker('!')

def run(args: argparse.Namespace) -> int:
    """ Run one or more gaames of pacman using pre-parsed arguments. """

    results = []
    for game in args._games:
        results.append(game.run(args._ui))

    scores = [result.score for result in results]
    wins = [(pacai.pacman.gamestate.PACMAN_AGENT_INDEX in result.winning_agent_indexes) for result in results]
    win_rate = wins.count(True) / float(len(wins))
    turn_counts = [len(result.history) for result in results]

    logging.info('Average Score: %s', sum(scores) / float(len(scores)))
    logging.info('Scores:        %s', ', '.join([str(score) for score in scores]))
    logging.info('Win Rate:      %d / %d (%0.2f)', wins.count(True), len(wins), win_rate)
    logging.info('Record:        %s', ', '.join([['Loss', 'Win'][int(win)] for win in wins]))
    logging.info('Average Turns: %s', sum(turn_counts) / float(len(turn_counts)))
    logging.info('Turn Counts:   %s', ', '.join([str(turn_count) for turn_count in turn_counts]))

    return 0

def set_cli_args(parser: argparse.ArgumentParser) -> None:
    """
    Set pacman-specific CLI arguments.
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

def _sprite_lookup(
        state: pacai.core.gamestate.GameState,
        sprite_sheet: pacai.core.spritesheet.SpriteSheet,
        marker: pacai.core.board.Marker | None = None,
        **kwargs) -> PIL.Image.Image:
    """ Pacman requires a special lookup function since ghosts need a special sprite when scared. """

    state = typing.cast(pacai.pacman.gamestate.GameState, state)
    if ((marker is not None)
            and (marker.is_agent())
            and (marker != pacai.pacman.gamestate.PACMAN_MARKER)
            and (state.is_scared(marker.get_agent_index()))):
        return sprite_sheet.get_sprite(marker = SCARED_GHOST_MARKER, **kwargs)

    return sprite_sheet.get_sprite(marker = marker, **kwargs)

def _parse_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    """ Parse the args from the parser returned by _get_parser(). """

    args = parser.parse_args()

    # Parse logging arguments.
    args = pacai.core.log.init_from_args(args)

    # Parse ui arguments.
    additional_ui_args = {
        'sprite_sheet_path': DEFAULT_SPRITE_SHEET,
        'sprite_lookup_func': _sprite_lookup,
    }
    args = pacai.core.ui.init_from_args(args, additional_args = additional_ui_args)

    # Parse pacman-specific options.
    base_agent_infos, remove_agent_indexes = init_from_args(args)

    # Parse game arguments.
    args = pacai.core.game.init_from_args(args, pacai.pacman.game.Game,
            base_agent_infos = base_agent_infos, remove_agent_indexes = remove_agent_indexes)

    return args

def _get_parser() -> argparse.ArgumentParser:
    """ Get a parser with all the options set to handle PacMan. """

    parser = argparse.ArgumentParser(description = "Play a game of Pac-Man.")

    # Add logging arguments.
    pacai.core.log.set_cli_args(parser)

    # Add UI arguments.
    pacai.core.ui.set_cli_args(parser)

    # Add game arguments.
    pacai.core.game.set_cli_args(parser, default_board = DEFAULT_BOARD)

    # Add pacman-specific options.
    set_cli_args(parser)

    return parser

def main() -> int:
    """ Invoke a game of PacMan. """

    args = _parse_args(_get_parser())
    return run(args)

if (__name__ == '__main__'):
    sys.exit(main())
