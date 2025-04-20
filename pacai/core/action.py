"""
The core actions that agents are allowed to take.
Default actions are provided, but custom actions can be easily created.
"""

import typing

import pacai.util.time

class Action(str):
    """ An action that an agent is allowed to take. """

    pass

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
EAST = Action("east")
SOUTH = Action("south")
WEST = Action("west")
STOP = Action("stop")
