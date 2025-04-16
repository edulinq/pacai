import pacai.core.action
import pacai.core.gamestate
import pacai.pacman.board

class GameState(pacai.core.gamestate.GameState):
    """ A game state specific to a standard Pacman game. """

    def __init__(self,
            score: int = 0,
            power_time: int = 0,
            food_count: int = 0,
            **kwargs) -> None:
        super().__init__(**kwargs)

        self.score: int = score
        """ Pacman's current score. """

        self.power_time: int = power_time
        """ The number of pacman turns the power capsule is active for. """

        self.food_count: int = food_count
        """ The number of food pellets on the board. """

    def get_legal_actions(self) -> list[pacai.core.action.Action]:
        if (self.agent_index == -1):
            return []

        position = self.get_agent_position()
        if (position is None):
            return []

        actions = [pacai.core.action.STOP]

        neighbor_moves = self.board.get_neighbors(position)
        for (action, position) in neighbor_moves:
            actions.append(action)

        return actions
