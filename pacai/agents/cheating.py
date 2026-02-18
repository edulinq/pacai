import typing

import pacai.core.action
import pacai.core.agent
import pacai.core.gamestate
import pacai.pacman.board

class CheatingAgent(pacai.core.agent.Agent):
    """
    This agent cheats!
    On its turn, this agent will try to modify the game state to declare itself the winner.
    Agent isolation should prevent this agent from cheating.
    """

    def get_action(self, state: pacai.core.gamestate.GameState) -> pacai.core.action.Action:
        state = typing.cast(pacai.pacman.gamestate.GameState, state)

        # Get a bunch of points.
        if (self.agent_index % 2 == 0):
            state.score = -1000
        else:
            state.score = 1000

        # Eat all the food, thereby winning the game.
        for food_position in state.get_food():
            state.board.remove_marker(pacai.pacman.board.MARKER_PELLET, food_position)

        # End the game.
        state.game_over = True

        return pacai.core.action.STOP
