import typing

import pacai.core.action
import pacai.core.agent
import pacai.core.features
import pacai.core.gamestate
import pacai.pacman.gamestate
import pacai.search.distance

CLOSE_GHOST_DISTANCE: float = 1.0
CLOSE_FOOD_DISTANCE: float = 0.0

def simple_feature_extractor(
        state: pacai.core.gamestate.GameState,
        action: pacai.core.action.Action,
        agent: pacai.core.agent.Agent | None = None,
        **kwargs: typing.Any) -> pacai.core.features.FeatureDict:
    """
    Get simple features for a basic reflex Pac-Man.

    Features:
     - 'bias' -- A constant value that allows a bias weight to be learned.
     - 'close-ghosts-count' -- The number of ghosts within CLOSE_GHOST_DISTANCE (may not always be present).
     - 'close-food-count' -- The number of food with CLOSE_FOOD_DISTANCE (may not always be present).
     - 'closest-food' -- A normalized distance to the closest food.
    """

    state = typing.cast(pacai.pacman.gamestate.GameState, state)

    agent_index = state.agent_index
    if (agent is not None):
        agent_index = agent.agent_index

    old_position = state.get_agent_position(agent_index)
    if (old_position is None):
        # If the agent is not on the board, return early.
        return pacai.core.features.FeatureDict({'bias': 0.1})

    new_position = old_position.apply_action(action)
    if (state.board.is_wall(new_position)):
        # If the action wants to put us out-of-bounds, return early.
        return pacai.core.features.FeatureDict({'bias': 0.1})

    features = pacai.core.features.FeatureDict()

    # Always add in a bias term.
    features['bias'] = 1.0

    distances = _get_distances(state, agent)
    max_distance = float(state.board.width * state.board.height)

    ghost_distances = [distances.get_distance_default(new_position, position, max_distance) for position in state.get_ghost_positions().values()]
    food_distances = [distances.get_distance_default(new_position, position, max_distance) for position in state.get_food()]

    close_ghosts = [distance for distance in ghost_distances if (distance <= CLOSE_GHOST_DISTANCE)]
    close_food = [distance for distance in food_distances if (distance <= CLOSE_FOOD_DISTANCE)]

    # If there are ghosts that are close, don't care about close food.
    if (len(close_ghosts) > 0):
        features['close-ghosts-count'] = len(close_ghosts)
    else:
        features['close-food-count'] = len(close_food)

    # Favor being close to food (don't count food we are eating).
    # Normalize by the max distance.
    closest_food = max_distance
    for food_distance in food_distances:
        closest_food = min(closest_food, food_distance)

    features['closest-food'] = closest_food / max_distance

    # Lower all features for better optimization.
    for (key, value) in list(features.items()):
        features[key] = value / 10.0

    return features

def _get_distances(
        state: pacai.core.gamestate.GameState,
        agent: pacai.core.agent.Agent | None = None) -> pacai.search.distance.DistancePreComputer:
    distances = None

    # If there is an agent, get precomputed distances from it.
    if (agent is not None):
        distances = agent.extra_storage.get('distances', None)

    # Compute distances if we have none.
    if (distances is None):
        distances = pacai.search.distance.DistancePreComputer()
        distances.compute(state.board)

    # Save the distances in the agent (if possible).
    if (agent is not None):
        agent.extra_storage['distances'] = distances

    return distances
