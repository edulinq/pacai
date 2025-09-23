import typing

import pacai.core.action
import pacai.core.agent
import pacai.core.agentaction
import pacai.core.gamestate

class UserInputAgent(pacai.core.agent.Agent):
    """
    An agent that makes moves based on input from a user.
    """

    def __init__(self,
            remember_last_action: bool = True,
            **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        self._remember_last_action: bool = remember_last_action
        """
        If no valid user action was provided, keep using the most recent valid action instead of just stopping.
        """

    def get_action_full(self,
            state: pacai.core.gamestate.GameState,
            user_inputs: list[pacai.core.action.Action],
            ) -> pacai.core.agentaction.AgentAction:
        legal_actions = state.get_legal_actions()

        # Specifically note if we used an input from the user.
        # If we did, then we can clear the input buffer.
        # This allows users to input actions without needing to be frame perfect,
        # e.g., a user can input a turn before the agent is in the intersection.
        used_user_input = False

        # If actions were provided, take the most recent one.
        intended_action = None
        if (len(user_inputs) > 0):
            intended_action = user_inputs[-1]
            used_user_input = True

            # If the intended action is not legal, then ignore it.
            if (intended_action not in legal_actions):
                intended_action = None
                used_user_input = False

        # If we got no legal input from the user, then assume the last action.
        if (self._remember_last_action and (intended_action is None)):
            intended_action = state.get_last_agent_action()
            used_user_input = False

        # If the action is illegal, then just stop (if legal) or pick a random action.
        if (intended_action not in legal_actions):
            if (pacai.core.action.STOP in legal_actions):
                intended_action = pacai.core.action.STOP
            else:
                intended_action = self.rng.choice(legal_actions)

            used_user_input = False

        return pacai.core.agentaction.AgentAction(intended_action, clear_inputs = used_user_input)
