import pacai.core.action
import pacai.core.gamestate
import pacai.core.search
import pacai.search.common

DEFAULT_GOAL_POSITION: pacai.core.board.Position = pacai.core.board.Position(1, 1)
DEFAULT_COST_FUNCTION: pacai.core.search.CostFunction = pacai.search.common.unit_cost_function

class PositionSearchNode(pacai.core.search.SearchNode):
    """
    A search node for the position search problem.
    The state for this problem is simple,
    it is just the current position being searched.
    """

    def __init__(self, position: pacai.core.board.Position) -> None:
        self.position = position
        """ The current position being searched. """

    def __eq__(self, other: object) -> bool:
        if (not isinstance(other, PositionSearchNode)):
            return False

        return self.position == other.position

    def __hash__(self) -> int:
        return hash(self.position)

class PositionSearchProblem(pacai.core.search.SearchProblem):
    """
    A search problem for finding a specific position on the board.
    """

    def __init__(self,
            game_state: pacai.core.gamestate.GameState,
            goal_position: pacai.core.board.Position | None = None,
            start_position: pacai.core.board.Position | None = None,
            cost_function: pacai.core.search.CostFunction | None = None,
            **kwargs) -> None:
        """
        Create a positional search problem.

        If no goal position is provided, the board's search target will be used,
            if that does not exist, then DEFAULT_GOAL_POSITION will be used.
        If no start position is provided, the current agent's position will be used.
        If no cost function is provided, DEFAULT_COST_FUNCTION will be used.
        """

        super().__init__()

        self._board = game_state.board
        """ Keep track of the board so we can navigate walls. """

        if (goal_position is None):
            if (self._board.search_target is not None):
                goal_position = self._board.search_target
            else:
                goal_position = DEFAULT_GOAL_POSITION

        self._goal_position = goal_position
        """ The position to search for. """

        if (start_position is None):
            start_position = game_state.get_agent_position()

        if (start_position is None):
            raise ValueError("Could not find starting position.")

        self.start_position = start_position
        """ The position to start from. """

        if (cost_function is None):
            cost_function = DEFAULT_COST_FUNCTION

        self._cost_function = cost_function
        """ The function used to score search nodes. """

    def get_starting_node(self) -> PositionSearchNode:
        return PositionSearchNode(self.start_position)

    def is_goal_node(self, node: PositionSearchNode) -> bool:  # type: ignore[override]
        return (self._goal_position == node.position)

    def complete(self, goal_node: PositionSearchNode) -> None:  # type: ignore[override]
        # Mark the final node in the history.
        self.position_history.append(goal_node.position)

    def get_successor_nodes(self, node: PositionSearchNode) -> list[pacai.core.search.SuccessorInfo]:  # type: ignore[override]
        successors = []

        # Check all the non-wall neighbors.
        for (action, position) in self._board.get_neighbors(node.position):
            next_node = PositionSearchNode(position)
            cost = self._cost_function(next_node)

            successors.append(pacai.core.search.SuccessorInfo(next_node, action, cost))

        # Do bookkeeping on the states/positions we visited.
        self.expanded_node_count += 1
        if (node not in self.visited_nodes):
            self.position_history.append(node.position)

        return successors
