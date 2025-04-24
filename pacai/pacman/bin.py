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
import pacai.pacman.ui.text
import pacai.ui.null
import pacai.ui.tk
import pacai.util.json

# TODO - Set fps if we have a UserInputAgent and fps is not already set.

DEFAULT_BOARD: str = 'medium-classic'

def run(args: argparse.Namespace) -> int:

    # board = pacai.core.board.load_path('pacai/resources/boards/medium-classic.txt')

    # ui = pacai.pacman.ui.text.StdioUI(fps = 10, animation_path = 'test.animation')
    # ui = pacai.ui.null.NullUI(animation_path = 'test.webp', animation_skip_frames = 3, animation_fps = 10, animation_optimize = True)
    # ui = pacai.ui.null.NullUI(animation_path = 'test.webp', animation_skip_frames = 3, animation_fps = 5, animation_optimize = False)
    # ui = pacai.ui.tk.TkUI(fps = 10)
    # ui = pacai.ui.tk.TkUI(fps = 10, animation_path = 'test2.webp', animation_skip_frames = 3, animation_fps = 10, animation_optimize = True)
    # game = pacai.pacman.game.Game(board, agent_args, seed = 4)

    result = args._game.run(args._ui)

    return 0

def _parse_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    args = parser.parse_args()

    # TEST: Game options (board and agent args as well)? Can check number of agents there and default enough agents (default to random).

    # TEST - Add specific arguments to set pacman and ghost agents.
    """
    parser.add_argument('-g', '--ghosts', dest = 'ghost',
            action = 'store', type = str, default = 'RandomGhost',
            help = 'use the specified ghostAgent module for the ghosts (default: %(default)s)')

    ''' TODO(eriq)
    parser.add_argument('--num-ghosts', dest = 'numGhosts',
            action = 'store', type = int, default = 4,
            help = 'set the maximum number of ghosts (default: %(default)s)')
    '''

    parser.add_argument('-p', '--pacman', dest = 'pacman',
            action = 'store', type = str, default = 'WASDKeyboardAgent',
            help = 'use the specified pacmanAgent module for pacman (default: %(default)s)')
    """

    # Parse logging arguments.
    args = pacai.core.log.init_from_args(args)

    # TEST
    base_agent_args: list[pacai.core.agent.AgentArguments | None] = [
        pacai.core.agent.AgentArguments(name = 'pacai.agents.userinput.UserInputAgent'),
        # pacai.core.agent.AgentArguments(name = 'pacai.agents.random.RandomAgent'),
        pacai.core.agent.AgentArguments(name = 'pacai.agents.random.RandomAgent'),
        pacai.core.agent.AgentArguments(name = 'pacai.agents.random.RandomAgent'),
    ]

    # Parse game arguments.
    args = pacai.core.game.init_from_args(args, pacai.pacman.game.Game, base_agent_args = base_agent_args)

    # Parse ui arguments.
    args = pacai.core.ui.init_from_args(args)

    return args

def _get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description = "Play a game of Pac-Man.")

    # Add logging arguments.
    pacai.core.log.set_cli_args(parser)

    # Add game arguments.
    pacai.core.game.set_cli_args(parser, default_board = DEFAULT_BOARD)

    # Add UI arguments.
    pacai.core.ui.set_cli_args(parser)

    return parser

def main() -> int:
    args = _parse_args(_get_parser())
    return run(args)

if (__name__ == '__main__'):
    sys.exit(main())
