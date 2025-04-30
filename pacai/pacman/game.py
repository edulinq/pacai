import random
import typing

import pacai.core.agentinfo
import pacai.core.board
import pacai.core.game
import pacai.core.gamestate
import pacai.pacman.gamestate

class Game(pacai.core.game.Game):
    """
    A game following the standard rules of PacMan.
    """

    def get_initial_state(self,
            rng: random.Random,
            board: pacai.core.board.Board,
            agent_infos: dict[int, pacai.core.agentinfo.AgentInfo]) -> pacai.core.gamestate.GameState:
        state = pacai.pacman.gamestate.GameState(board = board, agent_infos = agent_infos)
        state.food_count = len(state.board.get_marker_positions(pacai.pacman.board.MARKER_PELLET))
        return state

    def game_complete(self, state: pacai.core.gamestate.GameState, result: pacai.core.game.GameResult) -> None:
        state = typing.cast(pacai.pacman.gamestate.GameState, state)
        if (state.food_count == 0):
            result.winning_agent_index = pacai.pacman.gamestate.PACMAN_AGENT_INDEX
        else:
            result.winning_agent_index = pacai.pacman.gamestate.FIRST_GHOST_AGENT_INDEX
