import pacai.core.action
import pacai.core.agent
import pacai.core.gamestate

LEFT: dict[pacai.core.action.Action, pacai.core.action.Action] = {
    pacai.core.action.NORTH: pacai.core.action.WEST,
    pacai.core.action.EAST: pacai.core.action.NORTH,
    pacai.core.action.SOUTH: pacai.core.action.EAST,
    pacai.core.action.WEST: pacai.core.action.SOUTH,
    pacai.core.action.STOP: pacai.core.action.NORTH,
}
"""
The progression of actions this agent is to take.
We generally turn left/counter-clockwise, but go north on a stop.
"""

RIGHT: dict[pacai.core.action.Action, pacai.core.action.Action] = {
    pacai.core.action.NORTH: pacai.core.action.EAST,
    pacai.core.action.EAST: pacai.core.action.SOUTH,
    pacai.core.action.SOUTH: pacai.core.action.WEST,
    pacai.core.action.WEST: pacai.core.action.NORTH,
    pacai.core.action.STOP: pacai.core.action.NORTH,
}
""" The opposite of LEFT, but still go north on a stop. """

class LeftTurnAgent(pacai.core.agent.Agent):
    """
    An agent that turns left (counter-clockwise) at every opportunity.
    Three lefts make a right, and two rights don't make a wrong.

    This agent will try the following actions in order of priority:
     - Turn Left
     - Keep Going Current Direction
     - Turn Right
     - Turn Around
     - Randomly Choose Legal Action
    """

    def get_action(self, state: pacai.core.gamestate.GameState) -> pacai.core.action.Action:
        legal_actions = state.get_legal_actions()

        previous_action = state.get_last_agent_action()

        # Default to north on a stop or for the first action.
        if ((previous_action is None) or (previous_action == pacai.core.action.STOP)):
            previous_action = pacai.core.action.NORTH

        next_action = LEFT[previous_action]

        if (next_action in legal_actions):
            return next_action

        if (previous_action in legal_actions):
            return previous_action

        next_action = RIGHT[previous_action]
        if (next_action in legal_actions):
            return next_action

        next_action = LEFT[LEFT[previous_action]]
        if (next_action in legal_actions):
            return next_action

        return self.rng.choice(legal_actions)
