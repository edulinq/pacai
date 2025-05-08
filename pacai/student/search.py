"""
In this file, you will implement generic search algorithms which are called by searching agents.
"""

import random

import pacai.core.search

def depth_first_search(
        problem: pacai.core.search.SearchProblem,
        heuristic: pacai.core.search.SearchHeuristic,
        rng: random.Random,
        **kwargs) -> pacai.core.search.SearchSolution:
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
        **kwargs) -> pacai.core.search.SearchSolution:
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
        **kwargs) -> pacai.core.search.SearchSolution:
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
        **kwargs) -> pacai.core.search.SearchSolution:
    """
    A pacai.core.search.SearchProblemSolver that implements A* search (pronounced "A Star search").
    This means that it will search nodes with a lower combined cost and heuristic first.
    See: https://en.wikipedia.org/wiki/A*_search_algorithm .
    """

    # *** Your Code Here ***
    raise NotImplementedError('astar_search')
