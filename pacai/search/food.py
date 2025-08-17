import typing

import pacai.core.board
import pacai.core.gamestate
import pacai.core.search

class FoodSearchNode(pacai.core.search.SearchNode):
    """
    A search node for the food search problem.
    The state for this search problem will be
    the current position and the remaining food positions.
    """

    def __init__(self,
            position: pacai.core.board.Position,
            remaining_food: typing.Iterable[pacai.core.board.Position]) -> None:
        self.position: pacai.core.board.Position = position
        """ The current position being searched. """

        self.remaining_food: tuple[pacai.core.board.Position, ...] = tuple(sorted(list(remaining_food)))
        """
        The food left to eat.
        This is kept sorted to ensure that underlying comparison checks run cleanly.
        """

    def __lt__(self, other: object) -> bool:
        if (not isinstance(other, FoodSearchNode)):
            return False

        return ((self.position, self.remaining_food) < (other.position, other.remaining_food))

    def __eq__(self, other: object) -> bool:
        if (not isinstance(other, FoodSearchNode)):
            return False

        return ((self.position == other.position) and (self.remaining_food == other.remaining_food))

    def __hash__(self) -> int:
        return hash((self.position, self.remaining_food))

class FoodSearchProblem(pacai.core.search.SearchProblem[FoodSearchNode]):
    """
    A search problem associated with finding the a path that collects all of the "food" in a game.
    """

    def __init__(self,
            game_state: pacai.core.gamestate.GameState,
            start_position: pacai.core.board.Position | None = None,
            **kwargs: typing.Any) -> None:
        """
        Create a food search problem.

        If no start position is provided, the current agent's position will be used.
        """

        super().__init__()

        self.state: pacai.core.gamestate.GameState = game_state
        """ Keep track of the enire game state. """

        if (start_position is None):
            start_position = game_state.get_agent_position()

        if (start_position is None):
            raise ValueError("Could not find starting position.")

        self.start_position = start_position
        """ The position to start from. """

    def get_starting_node(self) -> FoodSearchNode:
        return FoodSearchNode(self.start_position, self.state.board.get_marker_positions(pacai.pacman.board.MARKER_PELLET))

    def is_goal_node(self, node: FoodSearchNode) -> bool:
        return (len(node.remaining_food) == 0)

    def complete(self, goal_node: FoodSearchNode) -> None:
        # Mark the final node in the history.
        self.position_history.append(goal_node.position)

    def get_successor_nodes(self, node: FoodSearchNode) -> list[pacai.core.search.SuccessorInfo]:
        successors = []

        # Check all the non-wall neighbors.
        for (action, position) in self.state.board.get_neighbors(node.position):
            new_remaining_food = list(node.remaining_food).copy()
            if (position in new_remaining_food):
                new_remaining_food.remove(position)

            next_node = FoodSearchNode(position, new_remaining_food)
            successors.append(pacai.core.search.SuccessorInfo(next_node, action, 1.0))

        # Do bookkeeping on the states/positions we visited.
        self.expanded_node_count += 1
        if (node not in self.visited_nodes):
            self.position_history.append(node.position)

        return successors
