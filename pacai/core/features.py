import typing

import pacai.core.action
import pacai.core.agent
import pacai.core.gamestate

FeatureDict: typing.TypeAlias = dict[str, float]
"""
A collection of features where each feature is keyed by a string.
This is a companion to WeightDict.

This is a simple alias for a Python dict with string keys and float values.
"""

WeightDict: typing.TypeAlias = dict[str, float]
"""
A collection of weights where each weight is keyed by a string.
This is a companion to FeatureDict.

This is a simple alias for a Python dict with string keys and float values.
"""

@typing.runtime_checkable
class FeatureExtractor(typing.Protocol):
    """
    A function that can be used to extract features from a game state and action pair.
    """

    def __call__(self,
            state: pacai.core.gamestate.GameState,
            action: pacai.core.action.Action,
            agent: pacai.core.agent.Agent | None = None,
            **kwargs: typing.Any) -> FeatureDict:
        """
        Extract the features for the given state/action pair.

        It is very important to note that we are not evaluating the current state,
        we are evaluating the state/action pair.
        A very common thing for extractors to do is to call generate_successor() on the state using the action,
        and then evaluate the successor state.
        This is a perfectly fine thing to do.
        The state and action are provided here as separate values for performance reasons.
        Extractors may be able to avoid copying states if they do not require a full successor.

        The optional agent may be used as a means of passing persistent state
        (like pre-computed distances) from the agent to this function.
        """

def score_feature_extractor(
        state: pacai.core.gamestate.GameState,
        action: pacai.core.action.Action,
        agent: pacai.core.agent.Agent | None = None,
        **kwargs: typing.Any) -> FeatureDict:
    """
    The most basic feature extractor, which just uses the state's current score.

    Features:
     - 'score' -- The current score of the game.
    """

    rng = None
    if (agent is not None):
        rng = agent.rng

    successor = state.generate_successor(action, rng = rng)

    features = FeatureDict()
    features['score'] = successor.score

    return features

def board_feature_extractor(
        state: pacai.core.gamestate.GameState,
        action: pacai.core.action.Action,
        agent: pacai.core.agent.Agent | None = None,
        **kwargs: typing.Any) -> FeatureDict:
    """
    A feature extractor that just creates a key unique to the board/action pair and assigns it a value of 1.0.
    It accomplishes this by generating a JSON string for all the non-wall objects in the board.
    This will be slow, and should generally not be used outside of learning applications.

    Features:
     - '<action::board>' -- A key unique to each action/board pair. The value is always 1.0.
    """

    key = f"{action}::{state.board.get_nonwall_string()}"

    features = FeatureDict()
    features[key] = 1.0

    return features
