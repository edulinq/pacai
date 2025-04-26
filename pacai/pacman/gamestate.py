import pacai.core.action
import pacai.core.gamestate
import pacai.pacman.board

class GameState(pacai.core.gamestate.GameState):
    """ A game state specific to a standard Pacman game. """

    def __init__(self,
            food_count: int = 0,
            scared_timers: dict[int, int] = {},
            **kwargs) -> None:
        super().__init__(**kwargs)

        self.food_count: int = food_count
        """ The number of food pellets on the board. """

        self.scared_timers: dict[int, int] = scared_timers
        """
        When pacman consumes a power pellet, each ghost get's scared for a specific amount of time.
        When a ghost dies their scared timer resets,
        so all ghosts need an independent timer.
        """

    def is_scared(self, agent_index: int = -1) -> bool:
        """ Check if the given agent (or the current agent) is currently scared. """

        if (agent_index == -1):
            agent_index = self.agent_index

        return self.scared_timers.get(agent_index, 0) > 0

    def get_legal_actions(self) -> list[pacai.core.action.Action]:
        if (self.agent_index == -1):
            raise ValueError("Cannot get legal actions when no agent is active.")

        actions = [pacai.core.action.STOP]

        position = self.get_agent_position()
        if (position is None):
            return actions

        neighbor_moves = self.board.get_neighbors(position)
        for (action, position) in neighbor_moves:
            actions.append(action)

        # Ghosts have special rules for their actions.
        if (self.agent_index > 0):
            self._get_ghost_legal_actions(actions)

        return actions

    def _get_ghost_legal_actions(self, actions: list[pacai.core.action.Action]) -> None:
        """
        Ghosts cannot stop (unless there are no other actions),
        and cannot turn around unless they reach a dead end (but can turn 90 degrees at intersections).
        """

        # Remove stop.
        if (pacai.core.action.STOP in actions):
            actions.remove(pacai.core.action.STOP)

        # Remove going backwards unless their are no other actions.
        last_action = self.last_agent_actions.get(self.agent_index, pacai.core.action.STOP)
        reverse_direction = self.get_reverse_action(last_action)
        if ((reverse_direction in actions) and (len(actions) > 1)):
            actions.remove(reverse_direction)

        # If we are not doing anything, then just stop.
        if (len(actions) == 0):
            actions.append(pacai.core.action.STOP)
