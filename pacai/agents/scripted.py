import typing

import pacai.core.action
import pacai.core.agent
import pacai.core.gamestate

ACTION_DELIM: str = ','

class ScriptedAgent(pacai.core.agent.Agent):
    """
    An agent that has a specific set of actions that they will do in order.
    Once the actions are exhausted, they will just stop.
    This agent will take a scripted action even if it is illegal.

    This agent is particularly useful for things like replays.
    """

    def __init__(self,
            actions: list[pacai.core.action.Action] | list[str] | str | None = None,
            **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        if (actions is None):
            actions = []

        if (isinstance(actions, str)):
            actions = actions.split(ACTION_DELIM)

        clean_actions = []
        for action in actions:
            clean_actions.append(pacai.core.action.Action(action))

        self._actions: list[pacai.core.action.Action] = clean_actions
        """ The scripted actions this agent will take. """

    def get_action(self, state: pacai.core.gamestate.GameState) -> pacai.core.action.Action:
        if (len(self._actions) > 0):
            return self._actions.pop(0)

        return pacai.core.action.STOP
