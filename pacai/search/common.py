"""
Common search utilities.
"""

import pacai.core.search

def unit_cost_function(node: pacai.core.search.SearchNode, **kwargs) -> float:
    """
    One of the most simple search functions,
    always return 1 (a single unit).
    """

    return 1.0

def null_heuristic(node: pacai.core.search.SearchNode, problem: pacai.core.search.SearchProblem, **kwargs) -> float:
    """ A trivial heuristic that returns a constant. """

    return 0.0
