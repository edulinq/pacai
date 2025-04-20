"""
The main executable for running a game of Pac-Man.
"""

import argparse
import sys

import pacai.core.agent
import pacai.core.board
import pacai.pacman.game
import pacai.pacman.ui.text
import pacai.util.json

# TODO - Set fps if we have a UserInputAgent and fps is not already set.

def run(args) -> int:
    agent_args = [
        pacai.core.agent.AgentArguments(name = 'pacai.agents.userinput.UserInputAgent'),
        pacai.core.agent.AgentArguments(name = 'pacai.agents.random.RandomAgent'),
        pacai.core.agent.AgentArguments(name = 'pacai.agents.random.RandomAgent'),
    ]

    board = pacai.core.board.load_path('pacai/boards/medium-classic.txt')

    ui = pacai.pacman.ui.text.Text(fps = 10)

    game = pacai.pacman.game.Game(agent_args)
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
