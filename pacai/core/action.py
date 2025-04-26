"""
The core actions that agents are allowed to take.
Default actions are provided, but custom actions can be easily created.
"""

import typing

import pacai.util.time

class Action(str):
    """ An action that an agent is allowed to take. """

    def __new__(cls, raw_text: str) -> 'Action':
        text = super().__new__(cls, raw_text.strip().upper())

        if (len(text) == 0):
            raise ValueError('Actions must not be empty.')

        return text

    def get_reverse_direction(self) -> typing.Union['Action', None]:
        """
        If this action is a cardinal direction, return the reveres direction.
        Returns None otherwise.
        """

        return REVERSE_CARDINAL_DIRECTIONS.get(self, None)

class ActionRecord(typing.NamedTuple):
    """
    The result of requesting an action from an agent.
    Aside from the action, this also includes timing and crashing information.
    """

    agent_index: int
    """ The index of the agent making this action. """

    action: Action
    """ The action returned by the agent (or pacai.core.action.STOP on a crash). """

    duration: pacai.util.time.Duration
    """ The duration (in MS) the agent took to compute this action. """

    crashed: bool
    """ Whether or not the agent crashed (e.g., raised an exception) when computing this action. """

NORTH = Action("north")
""" The action for moving north/up. """

EAST = Action("east")
""" The action for moving east/right. """

SOUTH = Action("south")
""" The action for moving south/down. """

WEST = Action("west")
""" The action for moving west/left. """

STOP = Action("stop")
"""
The action for moving stopping and not doing anything.
This action is often used as a catchall and should always be valid in most games.
"""


CARDINAL_DIRECTIONS: list[Action] = [
    NORTH,
    EAST,
    SOUTH,
    WEST,
]
""" The four main directions. """

REVERSE_CARDINAL_DIRECTIONS: dict[Action, Action] = {
    NORTH: SOUTH,
    EAST: WEST,
    SOUTH: NORTH,
    WEST: EAST,
}
""" The reverse of the four main directions. """
