"""
This file provides the core infrastructure for search problems.
"""

import abc
import random
import typing

import pacai.core.action
import pacai.core.board
import pacai.util.comparable

class SolutionNotFoundError(Exception):
    """ An error for when a search problem solver cannot find a solution. """

class SearchNode(abc.ABC, pacai.util.comparable.SimpleComparable):
    """
    A node or "state" in a search problem/tree.
    A search node represents one possible state of the problem.

    It is common to refer to search nodes as "search states" or "states".
    To avoid confusion with game states, this project will use "node" when referencing search problems.
    """

NodeType = typing.TypeVar('NodeType', bound = SearchNode)  # pylint: disable=invalid-name

class SuccessorInfo(typing.Generic[NodeType]):
    """
    A possible search node (and related information) that can be reached from another node in a search problem.
    """

    def __init__(self,
            node: NodeType,
            action: pacai.core.action.Action,
            cost: float,
            **kwargs: typing.Any) -> None:
        self.node = node
        """ The search node of this successor. """

        self.action = action
        """ The action that was taken at the old node to reach this successor. """

        self.cost = cost
        """ The cost of taken the action that lead to this successor. """

class SearchProblem(abc.ABC, typing.Generic[NodeType]):
    """
    This class outlines the structure of a search problem.
    Any search problem will need to provide answers to the following questions:
    1) Where should the search start?
    2) Is some specific search node a goal (are we done?)?
    3) What moves are possible from a given search node?

    The answers to these questions are provided by implementing
    the methods of this class.
    """

    def __init__(self, **kwargs: typing.Any) -> None:
        self.expanded_node_count: int = 0
        """
        The number of search nodes that have been expended.
        It is important that subclasses accurately keep this count up-to-date.
        """

        self.visited_nodes: set[NodeType] = set()
        """
        Keep track of the board positions that have been visited.
        This can help agents quickly check where they have previously been.
        """

        self.position_history: list[pacai.core.board.Position] = []
        """
        Keep track of the order that positions have been visited.
        This let's us know exactly how the agent has moved about.
        """

    def complete(self, goal_node: NodeType) -> None:
        """ Notify this search problem that the solver choose this goal node. """

    @abc.abstractmethod
    def get_starting_node(self) -> NodeType:
        """ Get the starting node for the search problem. """

    @abc.abstractmethod
    def is_goal_node(self, node: NodeType) -> bool:
        """ Check if this node is a valid goal node. """

    @abc.abstractmethod
    def get_successor_nodes(self, node: NodeType) -> list[SuccessorInfo[NodeType]]:
        """
        Get all the possible successors (successor nodes) to the current node.
        This action can be though of expanding a search node,
        or getting the children of a node in the search tree.
        """

class SearchSolution(typing.Generic[NodeType]):
    """
    A potential solution to a search problem.
    This does not have to be an optimal (or even correct) solution,
    but just what a solver returns.
    """

    def __init__(self,
            actions: list[pacai.core.action.Action],
            cost: float,
            goal_node: NodeType | None = None,
            ) -> None:
        self.actions: list[pacai.core.action.Action] = actions
        """
        The actions to take for this solution.
        These actions should guide the agent from its starting location (SearchProblem.get_starting_node())
        to the goal (SearchProblem.is_goal_node()).
        If the agent is just moving, you can think of this as it's "path".
        """

        self.cost: float = cost
        """ The cost of this solution. """

        self.goal_node: NodeType | None = goal_node
        """
        The node that the search was ended on.
        May be None in cases where the solver does not use search nodes.
        """

    def get_path(self, start_position: pacai.core.board.Position) -> list[pacai.core.board.Position]:
        """
        Given the starting locatrion, get the path this search solution represents.
        The resulting path will start at the starting position.
        It is assumed that unknown actions will not result in a move.
        """

        path = [start_position]

        for action in self.actions:
            path.append(path[-1].apply_action(action))

        return path

@typing.runtime_checkable
class CostFunction(typing.Protocol):
    """
    A function that computes the cost associated with a specific search node.
    """

    def __call__(self, node: SearchNode, **kwargs: typing.Any) -> float:
        ...

@typing.runtime_checkable
class SearchHeuristic(typing.Protocol):
    """
    A heuristic function attempts to score a search node in the context of a problem.
    """

    def __call__(self, node: SearchNode, problem: SearchProblem, **kwargs: typing.Any) -> float:
        ...

@typing.runtime_checkable
class SearchProblemSolver(typing.Protocol):
    """
    A function that solves a search problem and returns a solution.
    Not all solvers will need to heuristic or RNG,
    but they will always be provided (even if the heuristic is a null heuristic).
    If no solution/path can be found, a SolutionNotFoundError exception should be raised.
    """

    def __call__(self,
            problem: SearchProblem,
            heuristic: SearchHeuristic,
            rng: random.Random,
            **kwargs: typing.Any) -> SearchSolution:
        ...
