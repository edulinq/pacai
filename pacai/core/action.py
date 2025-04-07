"""
The core actions that agents are allowed to take.
Default actions are provided, but custom actions can be easily created.
"""

class Action(str):
    """ An action that an agent is allowed to take. """

    pass

NORTH = Action("north")
EAST = Action("east")
SOUTH = Action("south")
WEST = Action("west")
STOP = Action("stop")
