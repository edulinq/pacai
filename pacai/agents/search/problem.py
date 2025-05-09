import logging

import pacai.core.action
import pacai.core.agent
import pacai.core.agentaction
import pacai.core.agentinfo
import pacai.core.gamestate
import pacai.search.common
import pacai.search.random
import pacai.search.position
import pacai.util.alias
import pacai.util.reflection
import pacai.util.time

DEFAULT_PROBLEM: str = pacai.util.alias.SEARCH_PROBLEM_POSITION.long
DEFAULT_SOLVER: str = pacai.util.alias.SEARCH_SOLVER_RANDOM.long
DEFAULT_HEURISTIC: str = pacai.util.alias.HEURISTIC_NULL.long

class SearchProblemAgent(pacai.core.agent.Agent):
    """
    An agent that works by first solving a searh problem (pacai.core.search.Problem),
    and then executing the path found during the search.
    """

    def __init__(self, agent_info: pacai.core.agentinfo.AgentInfo, *args, **kwargs) -> None:
        """
        Create a SearchProblemAgent.

        Additional agent arguments are:
         - `problem: str` - A reflection reference to the search problem (pacai.core.search.SearchProblem) for this agent.
                            Defaults to DEFAULT_PROBLEM.
         - `solver: str` - A reflection reference to the problem solver (pacai.core.search.SearchProblemSolver) for this agent.
                            Defaults to DEFAULT_SOLVER.
         - `heuristic: str` - A reflection reference to the optional heuristic (pacai.core.search.SearchHeuristic) for this solver.
                            Defaults to DEFAULT_HEURISTIC.
        """

        super().__init__(agent_info, *args, **kwargs)

        problem_reference = pacai.util.reflection.Reference(agent_info.extra_arguments.get('problem', DEFAULT_PROBLEM))

        self._problem_class: type[pacai.core.search.SearchProblem] = pacai.util.reflection.fetch(problem_reference)
        """ The search problem class this agent will use. """

        solver_reference = pacai.util.reflection.Reference(agent_info.extra_arguments.get('solver', DEFAULT_SOLVER))

        self._solver_function: pacai.core.search.SearchProblemSolver = pacai.util.reflection.fetch(solver_reference)
        """ The search solver function this agent will use. """

        heuristic_reference = pacai.util.reflection.Reference(agent_info.extra_arguments.get('heuristic', DEFAULT_HEURISTIC))

        self._heuristic_function: pacai.core.search.SearchHeuristic = pacai.util.reflection.fetch(heuristic_reference)
        """ The search heuristic function this agent will use. """

        self._actions: list[pacai.core.action.Action] = []
        """ The actions that the search solver came up with. """

        logging.info("Created a SearchProblemAgent using problem '%s', solver '%s', and heuristic '%s'.",
                problem_reference, solver_reference, heuristic_reference)

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

        start_time = pacai.util.time.now()

        search_problem = self._problem_class(game_state = initial_state)
        solution = self._solver_function(search_problem, self._heuristic_function, self._rng)

        if (solution.goal_node is not None):
            search_problem.complete(solution.goal_node)

        end_time = pacai.util.time.now()

        self._actions = solution.actions

        logging.info("Path found with %d steps and a total cost of %0.2f in %0.2f seconds. %d search nodes expanded.",
                len(solution.actions), solution.cost, (end_time.sub(start_time).to_secs()), search_problem.expanded_node_count)

        # Highlight visited locations in the UI to visually represent our search pattern.
        highlights = []
        for (i, position) in enumerate(search_problem.position_history):
            # Gradually increase the highlight intensity from the start to the end.
            intensity = (i + 1) / len(search_problem.position_history)

            highlights.append(pacai.core.board.Highlight(position, intensity))

        return pacai.core.agentaction.AgentAction(board_highlights = highlights)
