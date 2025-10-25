"""
This file provides the core infrastructure for Markov Decision Processes (MDPs).
"""

import abc
import math
import typing

import edq.util.json

import pacai.core.action
import pacai.core.board
import pacai.core.gamestate
import pacai.util.comparable

ACTION_EXIT: pacai.core.action.Action = pacai.core.action.Action('exit')
""" A new action for exiting the MDP (used to reach the true terminal state). """

TERMINAL_POSITION: pacai.core.board.Position = pacai.core.board.Position(-1, -1)
""" A special (impossible) position representing the terminal state. """

class MDPState(edq.util.json.DictConverter):
    """
    A state or "node" in an MDP.
    """

    @abc.abstractmethod
    def is_terminal(self) -> bool:
        """ Whether or not this state is the terminal state. """

class MDPStatePosition(MDPState):
    """
    An MDP state that relies solely on position.

    Because this class is fairly high-traffic (and MDPStateBoard can be large),
    this class will prefer optimization over generalization.
    """

    def __init__(self,
            position: pacai.core.board.Position | dict[str, typing.Any] | None = None,
            **kwargs: typing.Any) -> None:
        if (position is None):
            raise ValueError("Cannot create a MDPStatePosition without a position.")

        if (isinstance(position, dict)):
            position = pacai.core.board.Position.from_dict(position)

        if (not isinstance(position, pacai.core.board.Position)):
            raise ValueError(f"Cannot create a MDPStatePosition with a non-position type: {type(position)}.")

        self.position: pacai.core.board.Position = position
        """ The board position of this MDP state. """

    def is_terminal(self) -> bool:
        return (self.position == TERMINAL_POSITION)

    def __lt__(self, other: 'MDPStatePosition') -> bool:  # type: ignore[override]
        return (self.position < other.position)

    def __eq__(self, other: object) -> bool:
        if (not isinstance(other, MDPStatePosition)):
            return False

        return (self.position == other.position)

    def __hash__(self) -> int:
        return self.position._hash

    def __str__(self) -> str:
        return str(self.position)

    def __repr__(self) -> str:
        return str(self)

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'position': self.position.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        return MDPStatePosition(data['position'])

class MDPStateBoard(MDPStatePosition):
    """
    An MDP state that uses an entire board.
    Technically, this only uses the non-wall markers for a board.

    Using this will be quite slow and is generally not recommended for larger problems.
    Because this class is fairly high-traffic (and the board data can be large),
    this class will prefer optimization over generalization.
    """

    def __init__(self,
            board: pacai.core.board.Board | None = None,
            game_state: pacai.core.gamestate.GameState | None = None,
            _board_string: str | None = None,
            **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        if (_board_string is None):
            if ((board is None) and (game_state is not None)):
                board = game_state.board

            if (board is None):
                raise ValueError("Cannot create a MDPStateBoard without a board.")

            _board_string = f"{self.position}::{board.get_nonwall_string()}"

        self._board_string: str = _board_string
        """
        The board represented as a string.
        Converting the board to a string makes future comparisons easier.
        """

    def __lt__(self, other: object) -> bool:
        if (not isinstance(other, MDPStateBoard)):
            return False

        return self._board_string < other._board_string

    def __eq__(self, other: object) -> bool:
        if (not isinstance(other, MDPStateBoard)):
            return False

        return self._board_string == other._board_string

    def __hash__(self) -> int:
        return hash(self._board_string)

    def __str__(self) -> str:
        return super().__str__() + "::" + str(hash(self))

    def __repr__(self) -> str:
        return str(self)

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            'position': self.position.to_dict(),
            '_board_string': self._board_string,
        }

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        return MDPStateBoard(position = data['position'], _board_string = data['_board_string'])

StateType = typing.TypeVar('StateType', bound = MDPState)  # pylint: disable=invalid-name

class Transition(typing.Generic[StateType]):
    """
    A possible result of taking some action in an MDP.
    """

    def __init__(self,
            state: StateType,
            action: pacai.core.action.Action,
            probability: float,
            reward: float,
            **kwargs: typing.Any) -> None:
        self.state = state
        """ The MDP state reached by this transition. """

        self.action = action
        """ The action taken to reach the given state. """

        self.probability = probability
        """ The probability that this transition will be taken. """

        self.reward = reward
        """ The reward for taking this transition. """

    def update(self, other: 'Transition', check: bool = True) -> None:
        """
        Add the probability from the other transition into this one.
        If check is true, then the states and rewards for these transitions must match.
        """

        if (check and (self.state != other.state)):
            raise ValueError(f"State of merging transitions does not match. Expected: '{self.state}', Found: '{other.state}'.")

        if (check and (not math.isclose(self.reward, other.reward))):
            raise ValueError(f"Reward of merging transitions does not match. Expected: '{self.reward}', Found: '{other.reward}'.")

        self.probability += other.probability

class MarkovDecisionProcess(typing.Generic[StateType], edq.util.json.DictConverter):
    """
    A class that implements a Markov Decision Process (MDP).

    See: https://en.wikipedia.org/wiki/Markov_decision_process .
    """

    def game_start(self, initial_game_state: pacai.core.gamestate.GameState) -> None:
        """
        Inform the MDP about the game's start.
        This is the MDP's first chance to see the game/board and initialize the appropriate data.
        """

    @abc.abstractmethod
    def get_starting_state(self) -> StateType:
        """ Return the starting state of this MDP. """

    @abc.abstractmethod
    def get_states(self) -> list[StateType]:
        """ Return a list of all states in this MDP. """

    @abc.abstractmethod
    def is_terminal_state(self, state: StateType) -> bool:
        """
        Returns true if the given state is a terminal state.
        By convention, a terminal state has zero future rewards.
        Sometimes the terminal state(s) may have no possible actions.
        It is also common to think of the terminal state as having
        a self-loop action 'pass' with zero reward; the formulations are equivalent.
        """

    @abc.abstractmethod
    def get_possible_actions(self, state: StateType) -> list[pacai.core.action.Action]:
        """ Return the possible actions from the given MDP state. """

    @abc.abstractmethod
    def get_transitions(self, state: StateType, action: pacai.core.action.Action) -> list[Transition[StateType]]:
        """
        Get a list of the possible transitions from the given state with the given action.
        A transition consists of the target state, the probability that the transition is taken,
        and the reward for taking that transition.

        All transition probabilities should add up to 1.0.

        Note that in some methods like Q-Learning and reinforcement learning,
        we do not know these probabilities nor do we directly model them.
        """

    def to_dict(self) -> dict[str, typing.Any]:
        return vars(self).copy()

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        return cls(**data)
