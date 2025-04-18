"""
The main executable for running a game of Pac-Man.
"""

import argparse
import sys

import pacai.core.agent
import pacai.core.board
import pacai.pacman.game
import pacai.util.json

def run(args) -> int:
    agent_args = [
        pacai.core.agent.AgentArguments(name = 'pacai.agents.random.RandomAgent'),
        pacai.core.agent.AgentArguments(name = 'pacai.agents.random.RandomAgent'),
        pacai.core.agent.AgentArguments(name = 'pacai.agents.random.RandomAgent'),
    ]

    board = pacai.core.board.load_path('pacai/boards/medium-classic.txt')

    game = pacai.pacman.game.Game(agent_args)
    result = game.run(board)

    # TEST
    print('###')
    print(pacai.util.json.dumps(result, indent = 4))
    print('###')

    return 0

def _get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description = "Run a game of Pac-Man.")

    return parser

def main() -> int:
    args = _get_parser().parse_args()
    return run(args)

if (__name__ == '__main__'):
    sys.exit(main())
