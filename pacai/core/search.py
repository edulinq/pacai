"""
This file provides the core infrastructure for search problems.
"""

import abc
import random
import typing

import pacai.core.action
import pacai.core.board

class SearchNode(abc.ABC):
    """
    A node or "state" in a search problem/tree.
    A search node represents one possible state of the problem.

    It is common to refer to search nodes as "search states" or "states".
    To avoid confusion with game states, this project will use "node" when referencing search problems.
    """

    @abc.abstractmethod
    def __eq__(self, other: object) -> bool:
        """ Override the default Python `==` operator so states can be used in dicts and sets. """

    @abc.abstractmethod
    def __hash__(self) -> int:
        """ Override the default Python hash function so states can be used in dicts and sets. """

class SuccessorInfo:
    """
    A possible search node (and related information) that can be reached from another node in a search problem.
    """

    def __init__(self,
            node: SearchNode,
            action: pacai.core.action.Action,
            cost: float,
            **kwargs) -> None:
        self.node = node
        """ The search node of this successor. """

        self.action = action
        """ The action that was taken at the old node to reach this successor. """

        self.cost = cost
        """ The cost of taken the action that lead to this successor. """

class SearchProblem(abc.ABC):
    """
    This class outlines the structure of a search problem.
    Any search problem will need to provide answers to the following questions:
    1) Where should the search start?
    2) Is some specific search node a goal (are we done?)?
    3) What moves are possible from a given search node?

    The answers to these questions are provided by implementing
    the methods of this class.
    """

    def __init__(self, **kwargs) -> None:
        self.expanded_node_count: int = 0
        """
        The number of search nodes that have been expended.
        It is important that subclasses accurately keep this count up-to-date.
        """

        self.visited_nodes: set[SearchNode] = set()
        """
        Keep track of the board positions that have been visited.
        This can help agents quickly check where they have previously been.
        """

        self.position_history: list[pacai.core.board.Position] = []
        """
        Keep track of the order that positions have been visited.
        This let's us know exactly how the agent has moved about.
        """

    @abc.abstractmethod
    def get_starting_node(self) -> SearchNode:
        """ Get the starting node for the search problem. """

    @abc.abstractmethod
    def is_goal_node(self, node: SearchNode) -> bool:
        """ Check if this node is a valid goal node. """

    def complete(self, goal_node: SearchNode) -> None:
        """ Notify this search problem that the soler choose this goal node. """

    @abc.abstractmethod
    def get_successor_nodes(self, node: SearchNode) -> list[SuccessorInfo]:
        """
        Get all the possible successors (successor nodes) to the current node.
        This action can be though of expanding a search node
        (where the passed in node is that search node).
        """

class SearchSolution:
    """
    A potential solution to a search problem.
    This does not have to be an optimal (or even correct) solution,
    but just what a solver returns.
    """

    def __init__(self, actions: list[pacai.core.action.Action], cost: float) -> None:
        self.actions: list[pacai.core.action.Action] = actions
        """
        The actions to take for this solution.
        These actions should guide the agent from its starting location (SearchProblem.get_starting_node())
        to the goal (SearchProblem.is_goal_node()).
        If the agent is just moving, you can think of this as it's "path".
        """

        self.cost: float = cost
        """ The cost of this solution. """

@typing.runtime_checkable
class CostFunction(typing.Protocol):
    """
    A function that computes the cost associated with a specific search node.
    """

    def __call__(self, node: SearchNode, **kwargs) -> float:
        ...

@typing.runtime_checkable
class SearchHeuristic(typing.Protocol):
    """
    A heuristic function attempts to score a search node in the context of a problem.
    """

    def __call__(self, node: SearchNode, problem: SearchProblem, **kwargs) -> float:
        ...

@typing.runtime_checkable
class SearchProblemSolver(typing.Protocol):
    """
    A function that solves a search problem and returns a solution.
    """

    def __call__(self,
            problem: SearchProblem,
            heuristic: SearchHeuristic,
            rng: random.Random,
            **kwargs) -> SearchSolution:
        ...
