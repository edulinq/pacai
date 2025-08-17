"""
The core actions that agents are allowed to take.
Default actions are provided, but custom actions can be easily created.
"""

import typing

class Action(str):
    """
    An action that an agent is allowed to take.

    Actions are just strings with no additional functionality.
    This type is more semantic than functional.
    """

    def __new__(cls, raw_text: str, safe: bool = False) -> 'Action':
        # If the caller deems the imput "safe" then we will skip all checks and cleaning,
        # and return just the input string.
        if (safe):
            return typing.cast('Action', raw_text)

        raw_text = raw_text.strip().upper()
        text = super().__new__(cls, raw_text)

        if (len(text) == 0):
            raise ValueError('Actions must not be empty.')

        return text

def get_reverse_direction(action: Action) -> Action | None:
    """
    If this action is a cardinal direction, return the reveres direction.
    Returns None otherwise.
    """

    return REVERSE_CARDINAL_DIRECTIONS.get(action, None)

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

CARDINAL_DIRECTION_ARROWS: dict[Action, str] = {
    NORTH: '↑',
    EAST: '→',
    SOUTH: '↓',
    WEST: '←',
}
""" Unicode arrows for the cardinal directions. """
