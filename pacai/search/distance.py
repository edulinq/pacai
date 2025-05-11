"""
This files contains functions and tools to computing and keeping track of distances between two positions on a board.
"""

import random
import typing

import pacai.core.board
import pacai.core.gamestate
import pacai.core.search
import pacai.search.common
import pacai.search.position
import pacai.search.random
import pacai.util.alias
import pacai.util.reflection

@typing.runtime_checkable
class DistanceFunction(typing.Protocol):
    """
    A function that computes the distance between two points.
    The game state is optional and will not apply to all distance functions.
    """

    def __call__(self,
            a: pacai.core.board.Position,
            b: pacai.core.board.Position,
            state: pacai.core.gamestate.GameState | None = None,
            **kwargs) -> float:
        ...

def manhattan_distance(
        a: pacai.core.board.Position,
        b: pacai.core.board.Position,
        state: pacai.core.gamestate.GameState | None = None,
        **kwargs) -> float:
    """
    Compute the Manhattan distance between two positions.
    See: https://en.wikipedia.org/wiki/Taxicab_geometry .
    """

    return abs(a.row - b.row) + abs(a.col - b.col)

def euclidean_distance(
        a: pacai.core.board.Position,
        b: pacai.core.board.Position,
        state: pacai.core.gamestate.GameState | None = None,
        **kwargs) -> float:
    """
    Compute the Euclidean distance between two positions.
    See: https://en.wikipedia.org/wiki/Euclidean_distance .
    """

    return ((a.row - b.row) ** 2 + (a.col - b.col) ** 2) ** 0.5

def maze_distance(
        a: pacai.core.board.Position,
        b: pacai.core.board.Position,
        state: pacai.core.gamestate.GameState | None = None,
        solver: pacai.core.search.SearchProblemSolver | str = pacai.util.alias.SEARCH_SOLVER_BFS.long,
        **kwargs) -> float:
    """
    Compute the "maze distance" between any two positions.
    This distance is the solution to a pacai.search.position.PositionSearchProblem between a and b.
    By default, BFS will be used to solve the search problem.
    If BFS is not implemented, then random search will be used.
    Note that random search can take a REALLY long time,
    so it is strongly recommended that you have BFS implemented before using this.
    """

    if (state is None):
        raise ValueError("Cannot compute maze distance without a game state.")

    # Make sure we are not starting in a wall.
    if (state.board.is_wall(a) or state.board.is_wall(b)):
        raise ValueError("Position for maze distance is inside a wall.")

    # Fetch our solver.
    if (isinstance(solver, str)):
        solver = pacai.util.reflection.fetch(solver)

    solver = typing.cast(pacai.core.search.SearchProblemSolver, solver)
    problem = pacai.search.position.PositionSearchProblem(state, goal_position = b, start_position = a)
    rng = random.Random(state.seed)

    try:
        solution = solver(problem, pacai.search.common.null_heuristic, rng)
        return len(solution.actions)
    except NotImplementedError:
        # If this solver is not implemented, fall back to random search.
        solution = pacai.search.random.random_search(problem, pacai.search.common.null_heuristic, rng)
        return len(solution.actions)

def distance_heuristic(
        node: pacai.core.search.SearchNode,
        problem: pacai.core.search.SearchProblem,
        distance_function: DistanceFunction = manhattan_distance,
        **kwargs) -> float:
    """
    A heuristic that looks for positional information in this search information,
    and returns the result of the given distance function if that information is found.
    Otherwise, the result of the null heuristic will be returned.

    In the search node, a "position" attribute of type pacai.core.board.Position will be checked,
    and in the search problem, a "goal_position" attribute of type pacai.core.board.Position will be checked.
    """

    if ((not hasattr(node, 'position')) or (not isinstance(getattr(node, 'position'), pacai.core.board.Position))):
        return pacai.search.common.null_heuristic(node, problem, **kwargs)

    if ((not hasattr(problem, 'goal_position')) or (not isinstance(getattr(problem, 'goal_position'), pacai.core.board.Position))):
        return pacai.search.common.null_heuristic(node, problem, **kwargs)

    a = getattr(node, 'position')
    b = getattr(problem, 'goal_position')

    return distance_function(a, b)

def manhattan_heuristic(
        node: pacai.core.search.SearchNode,
        problem: pacai.core.search.SearchProblem,
        **kwargs) -> float:
    """
    A distance_heuristic using Manhattan distance.
    """

    return distance_heuristic(node, problem, manhattan_distance, **kwargs)

def euclidean_heuristic(
        node: pacai.core.search.SearchNode,
        problem: pacai.core.search.SearchProblem,
        **kwargs) -> float:
    """
    A distance_heuristic using Euclidean distance.
    """

    return distance_heuristic(node, problem, euclidean_distance, **kwargs)
