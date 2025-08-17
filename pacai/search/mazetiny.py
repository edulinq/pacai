import random
import typing

import pacai.core.search

def maze_tiny_search(
        problem: pacai.core.search.SearchProblem,
        heuristic: pacai.core.search.SearchHeuristic,
        rng: random.Random,
        **kwargs: typing.Any) -> pacai.core.search.SearchSolution:
    """
    Output a very specific set of actions meant for the `maze-tiny` board.
    This (fake) search will generally not work on other boards.
    """

    actions = [
        pacai.core.action.SOUTH,
        pacai.core.action.SOUTH,
        pacai.core.action.WEST,
        pacai.core.action.SOUTH,
        pacai.core.action.WEST,
        pacai.core.action.WEST,
        pacai.core.action.SOUTH,
        pacai.core.action.WEST,
    ]

    return pacai.core.search.SearchSolution(actions, 0.0)
