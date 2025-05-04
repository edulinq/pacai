"""
This module handles containers for passing information from agents back to the game (via isolators).
"""

import typing

import pacai.core.action
import pacai.core.board
import pacai.util.json
import pacai.util.time

MIN_INTENSITY: int = 0
MAX_INTENSITY: int = 1000

class BoardHighlight(pacai.util.json.DictConverter):
    """
    A class representing a request to highlight/emphasize a position on the board.
    """

    def __init__(self,
            position: pacai.core.board.Position,
            intensity: int | float | None,
            ) -> None:
        self.position = position
        """ The position of this highlight. """

        if (isinstance(intensity, float)):
            if ((intensity < 0.0) or (intensity > 1.0)):
                raise ValueError(f"Floating point highlight intensity must be in [0.0, 1.0], found: {intensity}.")

            intensity = int(intensity * MAX_INTENSITY)

        if (isinstance(intensity, int)):
            if ((intensity < MIN_INTENSITY) or (intensity > MAX_INTENSITY)):
                raise ValueError(f"Integer highlight intensity must be in [MIN_INTENSITY, MAX_INTENSITY], found: {intensity}.")

        self.intensity: int | None = intensity
        """
        The highlight intensity associated with this position,
        or None if this highlight should be cleared.
        """

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'position': self.position.to_dict(),
            'intensity': self.intensity,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        data = {
            'position': pacai.core.board.Position.from_dict(data['position']),
            'intensity': data['intensity'],
        }
        return cls(**data)

class AgentAction(pacai.util.json.DictConverter):
    """
    The full response by an agent when an action is requested.
    Agent's usually just provide actions, but more information can be supplied if necessary.
    """

    def __init__(self,
            action: pacai.core.action.Action,
            board_highlights: list[BoardHighlight] | None = None,
            other_info: dict[str, typing.Any] | None = None,
            ) -> None:
        self.action: pacai.core.action.Action = action
        """ The action returned by the agent (or pacai.core.action.STOP on a crash). """

        if (board_highlights is None):
            board_highlights = []

        self.board_highlights: list[BoardHighlight] = board_highlights
        """
        Board highlights that the agent would like to take effect.
        """

        if (other_info is None):
            other_info = {}

        self.other_info: dict[str, typing.Any] = other_info
        """
        Additional information that the agent wishes to pass to the game.
        Specific games may use or ignore this information.
        """

    def to_dict(self) -> dict[str, typing.Any]:
        data = vars(self).copy()
        data['board_highlights'] = [board_highlight.to_dict() for board_highlight in self.board_highlights]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        data = data.copy()
        data['board_highlights'] = [BoardHighlight.from_dict(raw_highligh) for raw_highligh in data['board_highlights']]
        return cls(**data)

class AgentActionRecord(pacai.util.json.DictConverter):
    """
    The full representation of requesting an action from an agent.
    In addition to the data supplied by the agent,
    this class contains administrative fields used to keep track of the agent.
    """

    def __init__(self,
            agent_index: int,
            agent_action: AgentAction | None,
            duration: pacai.util.time.Duration,
            crashed: bool,
            ) -> None:
        self.agent_index: int = agent_index
        """ The index of the agent making this action. """

        self.agent_action: AgentAction | None = agent_action
        """ The information returned by the agent or None on a crash or timeout. """

        self.duration: pacai.util.time.Duration = duration
        """ The duration (in MS) the agent took to compute this action. """

        self.crashed: bool = crashed
        """ Whether or not the agent crashed (e.g., raised an exception) when computing this action. """

    def get_action(self) -> pacai.core.action.Action:
        """ Get the agent's action, or pacai.core.action.STOP if there is no action. """

        if (self.agent_action is None):
            return pacai.core.action.STOP

        return self.agent_action.action

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'agent_index': self.agent_index,
            'agent_action': self.agent_action.to_dict() if (self.agent_action is not None) else None,
            'duration': self.duration,
            'crashed': self.crashed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        return cls(
            agent_index = data['agent_index'],
            agent_action = AgentAction.from_dict(data['agent_action']) if data['agent_action'] is not None else None,
            duration = pacai.util.time.Duration(data['duration']),
            crashed = data['crashed'],
        )
