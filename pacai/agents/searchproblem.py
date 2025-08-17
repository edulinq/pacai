import logging
import typing

import edq.util.time

import pacai.core.action
import pacai.core.agent
import pacai.core.agentaction
import pacai.core.agentinfo
import pacai.core.board
import pacai.core.gamestate
import pacai.core.search
import pacai.search.common
import pacai.search.random
import pacai.search.position
import pacai.util.alias
import pacai.util.reflection

DEFAULT_PROBLEM: str = pacai.util.alias.SEARCH_PROBLEM_POSITION.long
DEFAULT_PROBLEM_COST: str = pacai.util.alias.COST_FUNC_UNIT.long
DEFAULT_SOLVER: str = pacai.util.alias.SEARCH_SOLVER_RANDOM.long
DEFAULT_HEURISTIC: str = pacai.util.alias.HEURISTIC_NULL.long

class SearchProblemAgent(pacai.core.agent.Agent):
    """
    An agent that works by first solving a searh problem (pacai.core.search.Problem),
    and then executing the path found during the search.
    """

    def __init__(self,
            problem: type[pacai.core.search.SearchProblem] | pacai.util.reflection.Reference | str = DEFAULT_PROBLEM,
            problem_cost: pacai.core.search.CostFunction | pacai.util.reflection.Reference | str = DEFAULT_PROBLEM_COST,
            solver: pacai.core.search.SearchProblemSolver | pacai.util.reflection.Reference | str = DEFAULT_SOLVER,
            heuristic: pacai.core.search.SearchHeuristic | pacai.util.reflection.Reference | str = DEFAULT_HEURISTIC,
            **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        claen_problem_class = pacai.util.reflection.resolve_and_fetch(type, problem)
        self._problem_class: type[pacai.core.search.SearchProblem] = claen_problem_class
        """ The search problem class this agent will use. """

        claen_problem_cost_function = pacai.util.reflection.resolve_and_fetch(pacai.core.search.CostFunction, problem_cost)
        self._problem_cost_function: pacai.core.search.CostFunction = claen_problem_cost_function
        """ The cost function for this agent's search problem. """

        claen_solver_function = pacai.util.reflection.resolve_and_fetch(pacai.core.search.SearchProblemSolver, solver)
        self._solver_function: pacai.core.search.SearchProblemSolver = claen_solver_function
        """ The search solver function this agent will use. """

        claen_heuristic_function = pacai.util.reflection.resolve_and_fetch(pacai.core.search.SearchHeuristic, heuristic)
        self._heuristic_function: pacai.core.search.SearchHeuristic = claen_heuristic_function
        """ The search heuristic function this agent will use. """

        self._actions: list[pacai.core.action.Action] = []
        """ The actions that the search solver came up with. """

        logging.debug("Created a SearchProblemAgent using problem '%s', cost function '%s', solver '%s', and heuristic '%s'.",
                pacai.util.reflection.get_qualified_name(problem),
                pacai.util.reflection.get_qualified_name(problem_cost),
                pacai.util.reflection.get_qualified_name(solver),
                pacai.util.reflection.get_qualified_name(heuristic))

    def get_action(self, state: pacai.core.gamestate.GameState) -> pacai.core.action.Action:
        if (len(self._actions) == 0):
            return pacai.core.action.STOP

        return self._actions.pop(0)

    def game_start_full(self,
            agent_index: int,
            suggested_seed: int,
            initial_state: pacai.core.gamestate.GameState,
            ) -> pacai.core.agentaction.AgentAction:
        # Do the standard game initialization steps.
        super().game_start_full(agent_index, suggested_seed, initial_state)

        # This is the agent's first time seeing the game's state (which includes the board).
        # Create a search problem using the game's state, and solve the problem.

        start_time = edq.util.time.Timestamp.now()
        (solution, position_history, expanded_node_count) = self._do_search(initial_state)
        end_time = edq.util.time.Timestamp.now()

        self._actions = solution.actions

        logging.info("Path found with %d steps and a total cost of %0.2f in %0.2f seconds. %d search nodes expanded.",
                len(solution.actions), solution.cost, (end_time.sub(start_time).to_secs()), expanded_node_count)

        # Highlight visited locations in the UI to visually represent our search pattern.
        highlights = []
        for (i, position) in enumerate(position_history):
            # Gradually increase the highlight intensity from the start to the end.
            intensity = (i + 1) / len(position_history)

            highlights.append(pacai.core.board.Highlight(position, intensity))

        return pacai.core.agentaction.AgentAction(board_highlights = highlights)

    def _do_search(self,
            state: pacai.core.gamestate.GameState,
            ) -> tuple[pacai.core.search.SearchSolution, list[pacai.core.board.Position], int]:
        """
        Perform the actual search operation.
        Children may override this to change searching behavior.
        Return: (solution, position history, expanded node count).
        """

        search_problem = self._problem_class(game_state = state, cost_function = self._problem_cost_function)
        solution = self._solver_function(search_problem, self._heuristic_function, self.rng)

        if (solution.goal_node is not None):
            search_problem.complete(solution.goal_node)

        return (solution, search_problem.position_history, search_problem.expanded_node_count)

class GreedySubproblemSearchAgent(SearchProblemAgent):
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
                state = state.generate_successor(action, self.rng)

        solution = pacai.core.search.SearchSolution(actions, total_cost, goal_node)
        return (solution, total_position_history, total_expanded_node_count)
