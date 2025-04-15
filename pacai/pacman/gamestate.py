import typing

import pacai.core.action
import pacai.core.gamestate
import pacai.pacman.board

class GameState(pacai.core.gamestate.GameState):
    """ A game state specific to a standard Pacman game. """

    def get_legal_actions(self) -> list[pacai.core.action.Action]:
        if (self.agent_index == -1):
            return []

        board = typing.cast(pacai.pacman.board.Board, self.board)

        position = board.get_agent_position(self.agent_index)
        if (position is None):
            return []

        actions = [pacai.core.action.STOP]

        neighbor_moves = self.board.get_neighbors(position)
        for (action, position) in neighbor_moves:
            actions.append(action)

        return actions
