# Feature extractors for Pacman game states and a private search problem to find
# the closest food.

import abc

from pacai.core import game
from pacai.core.game import Actions
from pacai.core.game import Directions
from pacai.core.search.problem import SearchProblem
from pacai.student import search
from pacai.util import counter

class FeatureExtractor(abc.ABC):
    @abc.abstractmethod
    def getFeatures(self, state, action):
        """
        Returns a dict from features to counts
        Usually, the count will just be 1.0 for
        indicator functions.
        """

        pass

class IdentityExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = counter.Counter()
        feats[(state, action)] = 1.0

        return feats

class SimpleExtractor(FeatureExtractor):
    """
    Returns simple features for a basic reflex Pacman:
        - whether food will be eaten
        - how far away the next food is
        - whether a ghost collision is imminent
        - whether a ghost is one step away
    """

    def getFeatures(self, state, action):
        # Extract the grid of food and wall locations and get the ghost locations.
        food = state.getFood()
        walls = state.getWalls()
        ghosts = state.getGhostPositions()

        features = counter.Counter()

        features["bias"] = 1.0

        # Compute the location of pacman after he takes the action.
        x, y = state.getPacmanPosition()
        dx, dy = game.Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        # Count the number of ghosts 1-step away.
        features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in
                game.Actions.getLegalNeighbors(g, walls) for g in ghosts)

        # If there is no danger of ghosts then add the food feature.
        if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
            features["eats-food"] = 1.0

        dist = _closestFood((next_x, next_y), food, walls)
        if dist is not None:
            # Make the distance a number less than one otherwise the update will diverge wildly.
            features["closest-food"] = float(dist) / (walls.width * walls.height)

        features.divideAll(10.0)
        return features

def _closestFood(pos, food, walls):
    """
    closestFood -- this is similar to the function that we have
    worked on in the search project; here its all in one place
    """

    x1, y1 = pos

    assert not walls[x1][y1]

    prob = _ClosestFoodSearchProblem(pos, food, walls)
    return len(search.bfs(prob))

class _ClosestFoodSearchProblem(SearchProblem):
    """
    A private search problem associated with finding the closest food
    from an initial position on the map.

    Search State: a tuple (x,y) representing the current position in the
    search
    """

    # Search problem requires the initial position to search from, the food
    # and walls on the map
    def __init__(self, initPos, food, walls):
        self._start = initPos
        self._foodGrid = food
        self._walls = walls

    def startingState(self):
        return self._start

    # Goal state is where the current position is at the same location as food
    def isGoal(self, state):
        return self._foodGrid[state[0]][state[1]]

    def successorStates(self, state):
        successors = []
        for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x, y = state
            dx, dy = Actions.directionToVector(direction)
            nextx, nexty = int(x + dx) + int(y + dy)
            if not self._walls[nextx][nexty]:
                successors.append((nextx, nexty))
        return successors

    def actionsCost(self, actions):
        x, y = self._start
        cost = 0
        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx) + int(y + dy)
            if self._walls[x][y]:
                return 999999
            cost += 1
        return cost
