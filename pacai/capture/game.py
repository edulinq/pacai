import random

import pacai.capture.gamestate
import pacai.core.agentinfo
import pacai.core.board
import pacai.core.game
import pacai.core.gamestate

class Game(pacai.core.game.Game):
    """
    A game following the standard rules of Capture.
    """

    def get_initial_state(self,
            rng: random.Random,
            board: pacai.core.board.Board,
            agent_infos: dict[int, pacai.core.agentinfo.AgentInfo]) -> pacai.core.gamestate.GameState:
        return pacai.capture.gamestate.GameState(board = board, agent_infos = agent_infos)
