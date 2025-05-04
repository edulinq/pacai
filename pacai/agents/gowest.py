import pacai.core.action
import pacai.core.agent
import pacai.core.gamestate

class GoWestAgent(pacai.core.agent.Agent):
    """ An agent that goes west as often as it can. """

    def get_action(self, state: pacai.core.gamestate.GameState) -> pacai.core.action.Action:
        """ Go west! """

        legal_actions = state.get_legal_actions()
        if (pacai.core.action.WEST in legal_actions):
            return pacai.core.action.WEST

        return pacai.core.action.STOP
