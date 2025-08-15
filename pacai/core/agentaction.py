"""
This module handles containers for passing information from agents back to the game (via isolators).
"""

import typing

import edq.util.json
import edq.util.time

import pacai.core.action
import pacai.core.board

class AgentAction(edq.util.json.DictConverter):
    """
    The full response by an agent when an action is requested.
    Agent's usually just provide actions, but more information can be supplied if necessary.
    """

    def __init__(self,
            action: pacai.core.action.Action = pacai.core.action.STOP,
            board_highlights: list[pacai.core.board.Highlight] | None = None,
            clear_inputs: bool = False,
            training_info: dict[str, typing.Any] | None = None,
            other_info: dict[str, typing.Any] | None = None,
            ) -> None:
        self.action: pacai.core.action.Action = action
        """ The action returned by the agent (or pacai.core.action.STOP on a crash). """

        if (board_highlights is None):
            board_highlights = []

        self.board_highlights: list[pacai.core.board.Highlight] = board_highlights
        """ Board highlights that the agent would like to take effect. """

        self.clear_inputs = clear_inputs
        """ Instruct the game that the agent has consumed the user inputs and any buffered inputs should be cleared. """

        if (training_info is None):
            training_info = {}

        self.training_info: dict[str, typing.Any] = training_info
        """
        Information about training that the agent wishes to pass to the game.
        Games may store this information and send it new subsequent agents on construction.

        All information put here must be trivially JSON serializable.
        """

        if (other_info is None):
            other_info = {}

        self.other_info: dict[str, typing.Any] = other_info
        """
        Additional information that the agent wishes to pass to the game.
        Specific games may use or ignore this information.

        All information put here must be trivially JSON serializable.
        """

    def to_dict(self) -> dict[str, typing.Any]:
        data = vars(self).copy()
        data['board_highlights'] = [board_highlight.to_dict() for board_highlight in self.board_highlights]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        data = data.copy()
        data['board_highlights'] = [pacai.core.board.Highlight.from_dict(raw_highligh) for raw_highligh in data['board_highlights']]
        return cls(**data)

class AgentActionRecord(edq.util.json.DictConverter):
    """
    The full representation of requesting an action from an agent.
    In addition to the data supplied by the agent,
    this class contains administrative fields used to keep track of the agent.
    """

    def __init__(self,
            agent_index: int,
            agent_action: AgentAction | None,
            duration: edq.util.time.Duration,
            crashed: bool = False,
            timeout: bool = False,
            ) -> None:
        self.agent_index: int = agent_index
        """ The index of the agent making this action. """

        self.agent_action: AgentAction | None = agent_action
        """ The information returned by the agent or None on a crash or timeout. """

        self.duration: edq.util.time.Duration = duration
        """ The duration (in MS) the agent took to compute this action. """

        self.crashed: bool = crashed
        """ Whether or not the agent crashed (e.g., raised an exception) when computing this action. """

        self.timeout: bool = timeout
        """ Whether or not the agent timed out when computing this action. """

    def get_action(self) -> pacai.core.action.Action:
        """ Get the agent's action, or pacai.core.action.STOP if there is no action. """

        if (self.agent_action is None):
            return pacai.core.action.STOP

        return self.agent_action.action

    def get_clear_inputs(self) -> bool:
        """ Get if the agent indicated that inputs should be cleated, or False if there is no action. """

        if (self.agent_action is None):
            return False

        return self.agent_action.clear_inputs

    def get_board_highlights(self) -> list[pacai.core.board.Highlight]:
        """ Get the board highlights. """

        if (self.agent_action is None):
            return []

        return self.agent_action.board_highlights

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'agent_index': self.agent_index,
            'agent_action': self.agent_action.to_dict() if (self.agent_action is not None) else None,
            'duration': self.duration,
            'crashed': self.crashed,
            'timeout': self.timeout,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        return cls(
            agent_index = data['agent_index'],
            agent_action = AgentAction.from_dict(data['agent_action']) if data['agent_action'] is not None else None,
            duration = edq.util.time.Duration(data['duration']),
            crashed = data.get('crashed', False),
            timeout = data.get('timeout', False),
        )
