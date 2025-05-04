import pacai.core.action
import pacai.core.agent
import pacai.core.gamestate

class CheatingAgent(pacai.core.agent.Agent):
    """
    This agent cheats!
    On its turn, this agent will try to modify the game state to declare itself the winner.
    Agent isolation should prevent this agent from cheating.
    """

    def get_action(self, state: pacai.core.gamestate.GameState) -> pacai.core.action.Action:
        # Get a bunch of points.
        state.score = 1000

        # Declare myself the winner (in pacman).
        if (hasattr(state, 'food_count')):
            setattr(state, 'food_count', 0)

        # End the game.
        state.game_over = True

        return pacai.core.action.STOP
