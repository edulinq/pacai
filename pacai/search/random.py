import random
import typing

import pacai.core.search

def random_search(
        problem: pacai.core.search.SearchProblem,
        heuristic: pacai.core.search.SearchHeuristic,
        rng: random.Random,
        **kwargs: typing.Any) -> pacai.core.search.SearchSolution:
    """
    Perform a random (and really stupid) search.
    Users should strive to implement better searches as soon as possible.
    """

    actions = []
    cost = 0.0

    # Start at the start.
    current_node = problem.get_starting_node()

    # Keep going until we get to the goal.
    while (not problem.is_goal_node(current_node)):
        successors = problem.get_successor_nodes(current_node)

        if (len(successors) == 0):
            raise ValueError("Unable to find solution.")

        # Randomly choose a successor.
        successor = rng.choice(successors)

        # Move to the next node.
        current_node = successor.node
        actions.append(successor.action)
        cost += successor.cost

    return pacai.core.search.SearchSolution(actions, cost, current_node)
