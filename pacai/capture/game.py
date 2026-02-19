import argparse
import random

import pacai.capture.gamestate
import pacai.core.agentinfo
import pacai.core.board
import pacai.core.game
import pacai.core.gamestate

RANDOM_BOARD_PREFIX: str = 'random'

class Game(pacai.core.game.Game):
    """
    A game following the standard rules of Capture.
    """

    def get_initial_state(self,
            rng: random.Random,
            board: pacai.core.board.Board,
            agent_infos: dict[int, pacai.core.agentinfo.AgentInfo]) -> pacai.core.gamestate.GameState:
        return pacai.capture.gamestate.GameState(board = board, agent_infos = agent_infos)

    @classmethod
    def override_args_with_replay(cls,
            args: argparse.Namespace, base_agent_infos: dict[int, pacai.core.agentinfo.AgentInfo]) -> None:
        super().override_args_with_replay(args, base_agent_infos)

        # Check for random boards.
        args.board = Game.check_for_random_board(args.board)

    @staticmethod
    def check_for_random_board(board: str) -> str | pacai.core.board.Board:
        """
        Check if the board string is a random board.
        If it is a board string represents a random board, generate and return it.
        If the board string is not random, return the original string.
        """

        if (not board.startswith(RANDOM_BOARD_PREFIX)):
            return board

        board_seed = None
        if (board != RANDOM_BOARD_PREFIX):
            # Strip 'random-' and 'random'.
            board_seed = int(board.removeprefix(RANDOM_BOARD_PREFIX + '-').removeprefix(RANDOM_BOARD_PREFIX))

        return pacai.capture.board.generate(seed = board_seed)
