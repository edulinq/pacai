"""
In this file, you will implement code relating to simple single-agent searches.
"""

import random
import typing

import pacai.agents.searchproblem
import pacai.core.agent
import pacai.core.agentaction
import pacai.core.board
import pacai.core.gamestate
import pacai.core.search
import pacai.pacman.board
import pacai.search.common
import pacai.search.food
import pacai.search.position

def depth_first_search(
        problem: pacai.core.search.SearchProblem,
        heuristic: pacai.core.search.SearchHeuristic,
        rng: random.Random,
        **kwargs: typing.Any) -> pacai.core.search.SearchSolution:
    """
    A pacai.core.search.SearchProblemSolver that implements depth first search (DFS).
    This means that it will search the deepest nodes in the search tree first.
    See: https://en.wikipedia.org/wiki/Depth-first_search .
    """

    # *** Your Code Here ***
    raise NotImplementedError('depth_first_search')

def breadth_first_search(
        problem: pacai.core.search.SearchProblem,
        heuristic: pacai.core.search.SearchHeuristic,
        rng: random.Random,
        **kwargs: typing.Any) -> pacai.core.search.SearchSolution:
    """
    A pacai.core.search.SearchProblemSolver that implements breadth first search (BFS).
    This means that it will search nodes based on what level in search tree they appear.
    See: https://en.wikipedia.org/wiki/Breadth-first_search .
    """

    # *** Your Code Here ***
    raise NotImplementedError('breadth_first_search')

def uniform_cost_search(
        problem: pacai.core.search.SearchProblem,
        heuristic: pacai.core.search.SearchHeuristic,
        rng: random.Random,
        **kwargs: typing.Any) -> pacai.core.search.SearchSolution:
    """
    A pacai.core.search.SearchProblemSolver that implements uniform cost search (UCS).
    This means that it will search nodes with a lower total cost first.
    See: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm#Practical_optimizations_and_infinite_graphs .
    """

    # *** Your Code Here ***
    raise NotImplementedError('uniform_cost_search')

def astar_search(
        problem: pacai.core.search.SearchProblem,
        heuristic: pacai.core.search.SearchHeuristic,
        rng: random.Random,
        **kwargs: typing.Any) -> pacai.core.search.SearchSolution:
    """
    A pacai.core.search.SearchProblemSolver that implements A* search (pronounced "A Star search").
    This means that it will search nodes with a lower combined cost and heuristic first.
    See: https://en.wikipedia.org/wiki/A*_search_algorithm .
    """

    # *** Your Code Here ***
    raise NotImplementedError('astar_search')

class CornersSearchNode(pacai.core.search.SearchNode):
    """
    A search node the can be used to represent the corners search problem.

    You get to implement this search node however you want.
    """

    def __init__(self) -> None:
        """ Construct a search node to help search for corners. """

        # *** Your Code Here ***
        # Remember that you can also add argument to your constructor.

class CornersSearchProblem(pacai.core.search.SearchProblem[CornersSearchNode]):
    """
    A search problem for touching the four different corners in a board.

    You may assume that very board is surrounded by walls (e.g., (0, 0) is a wall),
    and that the position diagonally inside from the walled corner is the location we are looking for.
    For example, if we had a square board that was 10x10, then we would be looking for the following corners:
     - (1, 1) -- North-West / Upper Left
     - (1, 8) -- North-East / Upper Right
     - (8, 1) -- South-West / Lower Left
     - (8, 8) -- South-East / Lower Right
    """

    def __init__(self,
            game_state: pacai.core.gamestate.GameState,
            **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        # *** Your Code Here ***

    def get_starting_node(self) -> CornersSearchNode:
        # *** Your Code Here ***
        raise NotImplementedError('CornersSearchProblem.get_starting_node')

    def is_goal_node(self, node: CornersSearchNode) -> bool:
        # *** Your Code Here ***
        raise NotImplementedError('CornersSearchProblem.is_goal_node')

    def get_successor_nodes(self, node: CornersSearchNode) -> list[pacai.core.search.SuccessorInfo]:
        # *** Your Code Here ***
        raise NotImplementedError('CornersSearchProblem.get_successor_nodes')

def corners_heuristic(node: CornersSearchNode, problem: CornersSearchProblem, **kwargs: typing.Any) -> float:
    """
    A heuristic for CornersSearchProblem.

    This function should always return a number that is a lower bound
    on the shortest path from the state to a goal of the problem;
    i.e. it should be admissible.
    (You need not worry about consistency for this heuristic to receive full credit.)
    """

    # *** Your Code Here ***
    return pacai.search.common.null_heuristic(node, problem)  # Default to a trivial solution.

def food_heuristic(node: pacai.search.food.FoodSearchNode, problem: pacai.search.food.FoodSearchProblem, **kwargs: typing.Any) -> float:
    """
    A heuristic for the FoodSearchProblem.
    """

    # *** Your Code Here ***
    return pacai.search.common.null_heuristic(node, problem)  # Default to a trivial solution.

class ClosestDotSearchAgent(pacai.agents.searchproblem.GreedySubproblemSearchAgent):
    """
    Search for a path to all the food by greedily searching for the next closest food again and again
    (util we have reached all the food).

    This agent is left to you to fill out.
    But make sure to take your time and think.
    The final solution is quite simple if you take your time to understand everything up until this point and leverage
    pacai.agents.searchproblem.GreedySubproblemSearchAgent and pacai.student.problem.AnyMarkerSearchProblem.
    pacai.agents.searchproblem.GreedySubproblemSearchAgent is already implemented,
    but you should take some time to understand it.
    pacai.student.problem.AnyMarkerSearchProblem (below in this file) has not yet been implemented,
    but is the quickest and easiest way to implement this class.

    Hint:
    Remember that you can call a parent class' `__init__()` method from a child class' `__init__()` method.
    (See pacai.student.problem.AnyMarkerSearchProblem for an example.)
    Child classes will generally always call their parent's `__init__()` method
    (if a child class does not implement `__init__()`, then the parent's `__init__()` is automatically called).
    This call does not need to be the first line in the method,
    and you can pass whatever you want to the parent's `__init__()`.
    """

    # *** Your Code Here ***

class AnyMarkerSearchProblem(pacai.search.position.PositionSearchProblem):
    """
    A search problem for finding a path to any instance of the specified board marker (e.g., food, wall, power capsule).

    This search problem is just like the pacai.search.position.PositionSearchProblem,
    but has a different goal test, which you need to fill in below.
    You may modify the `__init__()` if you want, the other methods should be fine as-is.
    """

    def __init__(self,
            game_state: pacai.core.gamestate.GameState,
            target_marker: pacai.core.board.Marker = pacai.pacman.board.MARKER_PELLET,
            **kwargs: typing.Any) -> None:
        super().__init__(game_state, **kwargs)

        # *** Your Code Here ***

    def is_goal_node(self, node: pacai.search.position.PositionSearchNode) -> bool:
        # *** Your Code Here ***
        raise NotImplementedError('CornersSearchProblem.is_goal_node')

class ApproximateSearchAgent(pacai.core.agent.Agent):
    """
    A search agent that tries to perform an approximate search instead of an exact one.
    In other words, this agent is okay with a solution that is "good enough" and not necessarily optimal.
    """
