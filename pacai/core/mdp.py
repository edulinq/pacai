"""
This file provides the core infrastructure for Markov Decision Processes (MDPs).
"""

import abc
import math
import typing

import pacai.core.action
import pacai.core.gamestate
import pacai.util.comparable
import pacai.util.json

class MDPState(pacai.util.comparable.SimpleComparable, pacai.util.json.DictConverter):
    """
    A state or "node" in an MDP.
    """

    @classmethod
    @abc.abstractmethod
    # Note that `typing.Self` is returned, but that is introduced in Python 3.12.
    def from_game_state(cls, game_state: pacai.core.gamestate.GameState, **kwargs) -> typing.Any:
        """ Create an instance of this MDP state from a game state. """

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
            **kwargs) -> None:
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

class MarkovDecisionProcess(typing.Generic[StateType], pacai.util.json.DictConverter):
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
