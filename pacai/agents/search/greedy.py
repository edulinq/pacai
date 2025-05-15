import pacai.agents.search.problem
import pacai.core.board
import pacai.core.gamestate
import pacai.core.search

class GreedySubproblemSearchAgent(pacai.agents.search.problem.SearchProblemAgent):
    """
    An agent that greedily solves several search problems (instead of just one main one).
    This agent will repeatedly create and solve search problems until the game state signals the game is over
    (pacai.core.gamestate.GameState.game_over == True).
    Once the goal is reached, the actions from all subproblem solutions will be concatenated to form the final list of actions.
    """

    def _do_search(self,
            state: pacai.core.gamestate.GameState,
            ) -> tuple[pacai.core.search.SearchSolution, list[pacai.core.board.Position], int]:
        actions = []
        total_cost = 0.0
        goal_node = None
        total_position_history = []
        total_expanded_node_count = 0

        while (not state.game_over):
            # Solve the subproblem.
            (solution, position_history, expanded_node_count) = super()._do_search(state)

            if (solution.goal_node is None):
                raise ValueError("Failed to solve subproblem.")

            # Add all the components of the sub-solution to the total solution.
            actions += solution.actions
            total_cost += solution.cost
            goal_node = solution.goal_node
            total_position_history += position_history
            total_expanded_node_count += expanded_node_count

            # Move to the next state by applying all the actions.
            for action in solution.actions:
                state = state.generate_successor(action)

        solution = pacai.core.search.SearchSolution(actions, total_cost, goal_node)
        return (solution, total_position_history, total_expanded_node_count)
