"""
The main executable for running a game of Pac-Man.
"""

import argparse
import sys

import pacai.core.agent
import pacai.core.board
import pacai.pacman.game
import pacai.pacman.ui.text
import pacai.ui.null
import pacai.util.json

# TODO - Set fps if we have a UserInputAgent and fps is not already set.

def run(args) -> int:
    agent_args = [
        # pacai.core.agent.AgentArguments(name = 'pacai.agents.userinput.UserInputAgent'),
        pacai.core.agent.AgentArguments(name = 'pacai.agents.random.RandomAgent'),
        pacai.core.agent.AgentArguments(name = 'pacai.agents.random.RandomAgent'),
        pacai.core.agent.AgentArguments(name = 'pacai.agents.random.RandomAgent'),
    ]

    board = pacai.core.board.load_path('pacai/resources/boards/medium-classic.txt')

    # ui = pacai.pacman.ui.text.StdioUI(fps = 10, animation_path = 'test.animation')
    ui = pacai.ui.null.NullUI(animation_path = 'test.webp', animation_skip_frames = 3, animation_fps = 20, animation_optimize = True)

    game = pacai.pacman.game.Game(agent_args, seed = 4)
    result = game.run(board, ui)

    return 0

def _get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description = "Run a game of Pac-Man.")

    return parser

def main() -> int:
    args = _get_parser().parse_args()
    return run(args)

if (__name__ == '__main__'):
    sys.exit(main())
