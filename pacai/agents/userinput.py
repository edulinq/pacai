import time

import pacai.core.action
import pacai.core.agent
import pacai.core.gamestate

class UserInputAgent(pacai.core.agent.Agent):
    """
    An agent that makes moves based on input from a user.
    """

    def __init__(self,
            agent_args: pacai.core.agent.AgentArguments,
            **kwargs) -> None:
        super().__init__(agent_args, *kwargs)

        self._last_action: pacai.core.action.Action = pacai.core.action.STOP
        """
        Keep track of the last action this agent took.
        If we don't get any input in the allotted time, we will repeat this action.
        """

    def get_action(self, state: pacai.core.gamestate.GameState, user_inputs: list[pacai.core.action.Action]) -> pacai.core.action.Action:
        # If actions were provided, take the most recent one.
        if (len(user_inputs) > 0):
            self._last_action = user_inputs[-1]

        # If the given action is not legal, then stop.
        legal_actions = state.get_legal_actions()
        if (self._last_action not in legal_actions):
            self._last_action = pacai.core.action.STOP

        return self._last_action

    def game_start(self, agent_index: int, suggested_seed: int, initial_state: pacai.core.gamestate.GameState) -> None:
        """ Do nothing. """

        pass

    def game_complete(self, final_state: pacai.core.gamestate.GameState) -> None:
        """ Do nothing. """

        pass
