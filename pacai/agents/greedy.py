import typing

import pacai.core.action
import pacai.core.agent
import pacai.core.gamestate
import pacai.core.features
import pacai.util.alias
import pacai.util.reflection

class GreedyAgent(pacai.core.agent.Agent):
    """
    An agent that greedily takes the available move with the best score at the time.
    If multiple moves have the same score, this agent will just randomly choose between them.
    """

    def get_action(self, state: pacai.core.gamestate.GameState) -> pacai.core.action.Action:
        legal_actions = state.get_legal_actions()
        if (len(legal_actions) == 1):
            return legal_actions[0]

        # Don't consider stopping unless we can do nothing else.
        if (pacai.core.action.STOP in legal_actions):
            legal_actions.remove(pacai.core.action.STOP)

        successors = [(state.generate_successor(action, self.rng), action) for action in legal_actions]
        scores = [(self.evaluate_state(successor, action = action), action) for (successor, action) in successors]

        best_score = max(scores)[0]
        best_actions = [pair[1] for pair in scores if pair[0] == best_score]

        return self.rng.choice(best_actions)

class GreedyFeatureAgent(GreedyAgent):
    """
    A greedy agent that uses weights and features to evaluate game states.
    Note that the states will already be successors.

    Children should set weights in the constructor,
    missing weights will be assumed to be 1.0.
    To compute custom features, children should either override compute_features()
    or pass in a pacai.core.features.FeatureExtractor on construction.
    """

    def __init__(self,
            feature_extractor_func: pacai.core.features.FeatureExtractor | pacai.util.reflection.Reference | str =
                    pacai.core.features.score_feature_extractor,
            **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        self.weights: pacai.core.features.WeightDict = pacai.core.features.WeightDict()
        """ The feature weights. """

        clean_feature_extractor_func = pacai.util.reflection.resolve_and_fetch(pacai.core.features.FeatureExtractor, feature_extractor_func)
        self.feature_extractor_func: pacai.core.features.FeatureExtractor = clean_feature_extractor_func
        """ The feature extractor that will be used to get features from a state. """

    def evaluate_state(self,
            state: pacai.core.gamestate.GameState,
            action: pacai.core.action.Action | None = None,
            **kwargs: typing.Any) -> float:
        if (action is None):
            action = pacai.core.action.STOP

        features = self.compute_features(state, action)

        score = 0.0
        for key, value in features.items():
            score += (self.weights.get(key, 0.0) * value)

        return score

    def compute_features(self,
            state: pacai.core.gamestate.GameState,
            action: pacai.core.action.Action,
            ) -> pacai.core.features.FeatureDict:
        """
        Compute the features to use for the given state/action pair.
        By default, the passed in feature extractor function will be used.
        """

        return self.feature_extractor_func(state, action, agent = self)
