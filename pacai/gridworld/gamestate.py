import pacai.core.action
import pacai.core.gamestate

AGENT_INDEX: int = 0
""" The index of the old agent. """

class GameState(pacai.core.gamestate.GameState):
    """ A game state specific to a standard GridWorld game. """

    def game_complete(self) -> list[int]:
        # TEST
        return []

    def process_turn(self, action: pacai.core.action.Action) -> None:
        # TEST
        # self.board.remove_marker(agent_marker, old_position)
        # self.board.place_marker(agent_marker, new_position)
        pass
