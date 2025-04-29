import time

import pacai.core.action
import pacai.core.agent
import pacai.core.agentinfo
import pacai.core.gamestate

class UserInputAgent(pacai.core.agent.Agent):
    """
    An agent that makes moves based on input from a user.
    """

    def __init__(self,
            agent_args: pacai.core.agentinfo.AgentInfo,
            **kwargs) -> None:
        super().__init__(agent_args, *kwargs)

        self._last_action: pacai.core.action.Action = pacai.core.action.STOP
        """
        Keep track of the last action this agent took.
        If we don't get any input in the allotted time, we will repeat this action.
        """

    def get_action(self, state: pacai.core.gamestate.GameState, user_inputs: list[pacai.core.action.Action]) -> pacai.core.action.Action:
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
            intended_action = self._last_action

        # If the action is illegal, then just stop.
        if (intended_action not in legal_actions):
            intended_action = pacai.core.action.STOP

        # Remember the last action.
        self._last_action = intended_action

        return self._last_action
