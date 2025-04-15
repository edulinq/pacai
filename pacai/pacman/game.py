import abc
import random

import pacai.core.agent
import pacai.core.board
import pacai.core.game
import pacai.core.gamestate
import pacai.pacman.gamestate

class Game(pacai.core.game.Game):
    """
    A game following the standard rules of PacMan.
    """

    def get_initial_state(self, rng: random.Random, board: pacai.core.board.Board) -> pacai.core.gamestate.GameState:
        return pacai.pacman.gamestate.GameState(board)

    @abc.abstractmethod
    def process_action(self, state: pacai.core.gamestate.GameState, action_record: pacai.core.agent.ActionRecord) -> pacai.core.gamestate.GameState:
        # TEST
        return state

    @abc.abstractmethod
    def check_end(self, state: pacai.core.gamestate.GameState) -> bool:
        # TEST
        return True
