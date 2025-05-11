import pacai.core.board
import pacai.core.gamestate
import pacai.core.search
import pacai.pacman.board
import pacai.search.common
import pacai.search.food
import pacai.search.position

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
            **kwargs) -> None:
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

def corners_heuristic(node: CornersSearchNode, problem: CornersSearchProblem, **kwargs) -> float:
    """
    A heuristic for CornersSearchProblem.

    This function should always return a number that is a lower bound
    on the shortest path from the state to a goal of the problem;
    i.e. it should be admissible.
    (You need not worry about consistency for this heuristic to receive full credit.)
    """

    # *** Your Code Here ***
    return pacai.search.common.null_heuristic(node, problem)  # Default to a trivial solution.

def food_heuristic(node: pacai.search.food.FoodSearchNode, problem: pacai.search.food.FoodSearchProblem, **kwargs) -> float:
    """
    A heuristic for the CornersSearchProblem.
    """

    # *** Your Code Here ***
    return pacai.search.common.null_heuristic(node, problem)  # Default to a trivial solution.

class AnyFoodSearchProblem(pacai.search.position.PositionSearchProblem):
    """
    A search problem for finding a path to any food.

    This search problem is just like the pacai.search.position.PositionSearchProblem,
    but has a different goal test, which you need to fill in below.
    The other methods should be fine as-is.

    Note that in the class definition above, `AnyFoodSearchProblem(pacai.search.position.PositionSearchProblem)`,
    this class inherits the methods of `pacai.search.position.PositionSearchProblem`.

    You can use this search problem to help you fill in
    the pacai.student.agent.ClosestDotSearchAgent.find_path_to_closest_dot method.
    """

    def __init__(self,
            game_state: pacai.core.gamestate.GameState,
            **kwargs) -> None:
        super().__init__(game_state, **kwargs)

        # Store the food positions for later reference.
        self.food: set[pacai.core.board.Position] = game_state.board.get_marker_positions(pacai.pacman.board.MARKER_PELLET)

    def is_goal_node(self, node: pacai.search.position.PositionSearchNode) -> bool:
        # *** Your Code Here ***
        raise NotImplementedError('CornersSearchProblem.is_goal_node')
