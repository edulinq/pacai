import typing

import pacai.agents.greedy
import pacai.core.action
import pacai.core.agent
import pacai.core.gamestate
import pacai.core.features
import pacai.search.distance

GHOST_IGNORE_RANGE: float = 2.5

class DefensiveAgent(pacai.agents.greedy.GreedyFeatureAgent):
    """
    A capture agent that prioritizes defending its own territory.
    """

    def __init__(self,
            override_weights: dict[str, float] | None = None,
            **kwargs: typing.Any) -> None:
        kwargs['feature_extractor_func'] = _extract_baseline_defensive_features
        super().__init__(**kwargs)

        self._distances: pacai.search.distance.DistancePreComputer = pacai.search.distance.DistancePreComputer()
        """ Precompute distances. """

        # Set base weights.
        self.weights['on_home_side'] = 100.0
        self.weights['stopped'] = -100.0
        self.weights['reverse'] = -2.0
        self.weights['num_invaders'] = -1000.0
        self.weights['distance_to_invader'] = -10.0

        if (override_weights is None):
            override_weights = {}

        for (key, weight) in override_weights.items():
            self.weights[key] = weight

    def game_start(self, initial_state: pacai.core.gamestate.GameState) -> None:
        self._distances.compute(initial_state.board)

class OffensiveAgent(pacai.agents.greedy.GreedyFeatureAgent):
    """
    A capture agent that prioritizes defending its own territory.
    """

    def __init__(self,
            override_weights: dict[str, float] | None = None,
            **kwargs: typing.Any) -> None:
        kwargs['feature_extractor_func'] = _extract_baseline_offensive_features
        super().__init__(**kwargs)

        self._distances: pacai.search.distance.DistancePreComputer = pacai.search.distance.DistancePreComputer()
        """ Precompute distances. """

        # Set base weights.
        self.weights['score'] = 100.0
        self.weights['distance_to_food'] = -1.0

        if (override_weights is None):
            override_weights = {}

        for (key, weight) in override_weights.items():
            self.weights[key] = weight

    def game_start(self, initial_state: pacai.core.gamestate.GameState) -> None:
        self._distances.compute(initial_state.board)

def _extract_baseline_defensive_features(
        state: pacai.core.gamestate.GameState,
        action: pacai.core.action.Action,
        agent: pacai.core.agent.Agent | None = None,
        **kwargs: typing.Any) -> pacai.core.features.FeatureDict:
    agent = typing.cast(DefensiveAgent, agent)
    state = typing.cast(pacai.capture.gamestate.GameState, state)

    features: pacai.core.features.FeatureDict = pacai.core.features.FeatureDict()

    current_position = state.get_agent_position(agent.agent_index)
    if (current_position is None):
        # We are dead and waiting to respawn.
        return features

    # Note the side of the board we are on.
    features['on_home_side'] = int(state.is_ghost(agent_index = agent.agent_index))

    # Prefer moving over stopping.
    features['stopped'] = int(action == pacai.core.action.STOP)

    # Prefer not turning around.
    # Remember that the state we get is already a successor, so we have to look two actions back.
    agent_actions = state.get_agent_actions(agent.agent_index)
    if (len(agent_actions) > 1):
        features['reverse'] = int(action == state.get_reverse_action(agent_actions[-2]))

    # We don't like any invaders on our side.
    invader_positions = state.get_invader_positions(agent_index = agent.agent_index)
    features['num_invaders'] = len(invader_positions)

    # Hunt down the closest invader!
    if (len(invader_positions) > 0):
        invader_distances = [agent._distances.get_distance(current_position, invader_position) for invader_position in invader_positions.values()]
        features['distance_to_invader'] = min(distance for distance in invader_distances if (distance is not None))

    return features

def _extract_baseline_offensive_features(
        state: pacai.core.gamestate.GameState,
        action: pacai.core.action.Action,
        agent: pacai.core.agent.Agent | None = None,
        **kwargs: typing.Any) -> pacai.core.features.FeatureDict:
    agent = typing.cast(OffensiveAgent, agent)
    state = typing.cast(pacai.capture.gamestate.GameState, state)

    features: pacai.core.features.FeatureDict = pacai.core.features.FeatureDict()
    features['score'] = state.get_normalized_score(agent.agent_index)

    # Note the side of the board we are on.
    features['on_home_side'] = int(state.is_ghost(agent_index = agent.agent_index))

    # Prefer moving over stopping.
    features['stopped'] = int(action == pacai.core.action.STOP)

    # Prefer not turning around.
    # Remember that the state we get is already a successor, so we have to look two actions back.
    agent_actions = state.get_agent_actions(agent.agent_index)
    if (len(agent_actions) > 1):
        features['reverse'] = int(action == state.get_reverse_action(agent_actions[-2]))

    current_position = state.get_agent_position(agent.agent_index)
    if (current_position is None):
        # We are dead and waiting to respawn.
        return features

    food_positions = state.get_food(agent_index = agent.agent_index)
    if (len(food_positions) > 0):
        food_distances = [agent._distances.get_distance(current_position, food_position) for food_position in food_positions]
        features['distance_to_food'] = min(distance for distance in food_distances if (distance is not None))
    else:
        # There is no food left, give a large score.
        features['distance_to_food'] = -100000

    ghost_positions = state.get_nonscared_opponent_positions(agent_index = agent.agent_index)
    if (len(ghost_positions) > 0):
        ghost_distances = [agent._distances.get_distance(current_position, ghost_position) for ghost_position in ghost_positions.values()]
        features['distance_to_ghost'] = min(distance for distance in ghost_distances if (distance is not None))
        if (features['distance_to_ghost'] > GHOST_IGNORE_RANGE):
            features['distance_to_ghost'] = 1000

        features['distance_to_ghost_squared'] = features['distance_to_ghost'] ** 2
    else:
        features['distance_to_ghost'] = 0

    return features
