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
        self.position = position
        """ The current position being searched. """

        self.remaining_food = list(sorted(list(remaining_food).copy()))
        """
        The food left to eat.
        This is kept sorted to ensure that underlying checks run cleanly
        (see pacai.core.search.SeachNode._to_json_string()).
        """

class FoodSearchProblem(pacai.core.search.SearchProblem[FoodSearchNode]):
    """
    A search problem associated with finding the a path that collects all of the "food" in a game.
    """

    def __init__(self,
            game_state: pacai.core.gamestate.GameState,
            **kwargs) -> None:
        super().__init__()

        self._state = game_state
        """ Keep track of the enire game state. """

    def get_starting_node(self) -> FoodSearchNode:
        position = self._state.get_agent_position()
        if (position is None):
            raise ValueError("Could not find starting agent position.")

        return FoodSearchNode(position, self._state.board.get_marker_positions(pacai.pacman.board.MARKER_PELLET))

    def is_goal_node(self, node: FoodSearchNode) -> bool:
        return (len(node.remaining_food) == 0)

    def complete(self, goal_node: FoodSearchNode) -> None:
        # Mark the final node in the history.
        self.position_history.append(goal_node.position)

    def get_successor_nodes(self, node: FoodSearchNode) -> list[pacai.core.search.SuccessorInfo]:
        successors = []

        # Check all the non-wall neighbors.
        for (action, position) in self._state.board.get_neighbors(node.position):
            new_remaining_food = node.remaining_food.copy()
            if (position in new_remaining_food):
                new_remaining_food.remove(position)

            next_node = FoodSearchNode(position, new_remaining_food)
            successors.append(pacai.core.search.SuccessorInfo(next_node, action, 1.0))

        # Do bookkeeping on the states/positions we visited.
        self.expanded_node_count += 1
        if (node not in self.visited_nodes):
            self.position_history.append(node.position)

        return successors
