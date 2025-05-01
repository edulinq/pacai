import pacai.core.action
import pacai.core.agent
import pacai.core.agentinfo
import pacai.core.gamestate

ACTIONS_KEY: str = 'actions'
""" The extra arguments key for the agent's scripted actions. """

DEFAULT_ACTIONS: list[str] = []
""" The default scripted actions (no actions). """

class ScriptedAgent(pacai.core.agent.Agent):
    """
    An agent that has a specific set of actions that they will do in order.
    Once the actions are exhausted, they will just stop.
    This agent will take a scripted action even if it is illegal.

    This agent is particularly useful for things like replays.
    """

    def __init__(self, agent_info: pacai.core.agentinfo.AgentInfo, *args, **kwargs) -> None:
        super().__init__(agent_info, *args, **kwargs)

        raw_actions = agent_info.extra_arguments.get(ACTIONS_KEY, DEFAULT_ACTIONS)

        self._actions: list[pacai.core.action.Action] = [pacai.core.action.Action(raw_action) for raw_action in raw_actions]
        """ The scripted actions this agent will take. """

    def get_action(self, state: pacai.core.gamestate.GameState, user_inputs: list[pacai.core.action.Action]) -> pacai.core.action.Action:
        if (len(self._actions) > 0):
            return self._actions.pop(0)

        return pacai.core.action.STOP
