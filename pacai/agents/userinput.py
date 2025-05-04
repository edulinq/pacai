import pacai.core.action
import pacai.core.agent
import pacai.core.agentaction
import pacai.core.gamestate

class UserInputAgent(pacai.core.agent.Agent):
    """
    An agent that makes moves based on input from a user.
    """

    def get_action_full(self,
            state: pacai.core.gamestate.GameState,
            user_inputs: list[pacai.core.action.Action],
            ) -> pacai.core.agentaction.AgentAction:
        legal_actions = state.get_legal_actions()

        # If actions were provided, take the most recent one.
        intended_action = None
        if (len(user_inputs) > 0):
            intended_action = user_inputs[-1]

            # If the intended action is not legal, then ignore it.
            if (intended_action not in legal_actions):
                intended_action = None

        # If we got no legal input from the user, then assume the last action.
        if (intended_action is None):
            intended_action = state.get_agent_last_action()

        # If the action is illegal, then just stop.
        if (intended_action not in legal_actions):
            intended_action = pacai.core.action.STOP

        return pacai.core.agentaction.AgentAction(intended_action)
