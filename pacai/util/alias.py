"""
This file provides useful aliases/shortcuts or short names for different objects in pacai.
For example, the `web` alias can be used to reference `pacai.ui.web.WebUI`.
"""

class Alias:
    """ An alias for some object name. """

    _alias_map: dict[str, str] = {}
    """ Keep track of all aliases for testing purposes. """

    _all_aliases: list['Alias'] = []
    """ Keep track of all aliases mappings for lookup. """

    def __init__(self,
            short: str, long: str,
            is_qualified_name: bool = True, skip_windows_test: bool = False,
            ) -> None:
        self.short: str = short
        """ The short name for this alias. """

        self.long: str = long
        """ The long name for this alias. """

        self.is_qualified_name: bool = is_qualified_name
        """
        Whether this alias represents a qualified name.
        Alias that are qualified names will be tested with reflection.
        """

        self.skip_windows_test: bool = skip_windows_test
        """ If this alias' reflection test should be skipped on Windows. """

        if ('.' in short):
            raise ValueError(f"Dots ('.') are not allowed in aliases. Found '{short}'.")

        if (short in Alias._alias_map):
            raise ValueError(f"Found duplicate alias: '{short}' -> '{long}'.")

        Alias._alias_map[short] = long
        Alias._all_aliases.append(self)

def lookup(short: str, default: str | None = None) -> str:
    """
    Lookup the long name for an alias.
    Return the alias long name if the alias is found,
    and the default value if the alias is not found.
    If the alias is not found and no default is specified,
    then raise an error.
    """

    if (short in Alias._alias_map):
        return Alias._alias_map[short]

    if (default is not None):
        return default

    raise ValueError(f"Could not find alias: '{short}'.")

AGENT_CHEATING: Alias = Alias('agent-cheating', 'pacai.agents.cheating.CheatingAgent')
AGENT_DUMMY: Alias = Alias('agent-dummy', 'pacai.agents.dummy.DummyAgent')
AGENT_GO_WEST: Alias = Alias('agent-go-west', 'pacai.agents.gowest.GoWestAgent')
AGENT_GREEDY: Alias = Alias('agent-greedy', 'pacai.agents.greedy.GreedyAgent')
AGENT_LEFT_TURN: Alias = Alias('agent-left-turn', 'pacai.agents.leftturn.LeftTurnAgent')
AGENT_MINIMAX: Alias = Alias('agent-minimax', 'pacai.student.multiagents.MyMinimaxLikeAgent')
AGENT_RANDOM: Alias = Alias('agent-random', 'pacai.agents.random.RandomAgent')
AGENT_REFLEX: Alias = Alias('agent-reflex', 'pacai.student.multiagents.ReflexAgent')
AGENT_SCRIPTED: Alias = Alias('agent-scripted', 'pacai.agents.scripted.ScriptedAgent')
AGENT_SEARCH_PROBLEM: Alias = Alias('agent-search-problem', 'pacai.agents.search.problem.SearchProblemAgent')
AGENT_SEARCH_CLOSEST_DOT: Alias = Alias('agent-search-closest-dot', 'pacai.student.singlesearch.ClosestDotSearchAgent')
AGENT_USER_INPUT: Alias = Alias('agent-user-input', 'pacai.agents.userinput.UserInputAgent')

AGENT_SHORT_NAMES: list[str] = [
    AGENT_CHEATING.short,
    AGENT_DUMMY.short,
    AGENT_GO_WEST.short,
    AGENT_GREEDY.short,
    AGENT_LEFT_TURN.short,
    AGENT_REFLEX.short,
    AGENT_RANDOM.short,
    AGENT_SCRIPTED.short,
    AGENT_SEARCH_PROBLEM.short,
    AGENT_SEARCH_CLOSEST_DOT.short,
    AGENT_USER_INPUT.short,
]

DISTANCE_EUCLIDEAN: Alias = Alias('distance-euclidean', 'pacai.search.distance.euclidean_distance')
DISTANCE_MANHATTAN: Alias = Alias('distance-manhattan', 'pacai.search.distance.manhattan_distance')
DISTANCE_MAZE: Alias = Alias('distance-maze', 'pacai.search.distance.maze_distance')

DISTANCE_SHORT_NAMES: list[str] = [
    DISTANCE_EUCLIDEAN.short,
    DISTANCE_MANHATTAN.short,
    DISTANCE_MAZE.short,
]

COST_FUNC_LONGITUDINAL: Alias = Alias('cost-longitudinal', 'pacai.search.common.longitudinal_cost_function')
COST_FUNC_STAY_EAST: Alias = Alias('cost-stay-east', 'pacai.search.common.stay_east_cost_function')
COST_FUNC_STAY_WEST: Alias = Alias('cost-stay-west', 'pacai.search.common.stay_west_cost_function')
COST_FUNC_UNIT: Alias = Alias('cost-unit', 'pacai.search.common.unit_cost_function')

COST_FUNC_SHORT_NAMES: list[str] = [
    COST_FUNC_LONGITUDINAL.short,
    COST_FUNC_STAY_EAST.short,
    COST_FUNC_STAY_WEST.short,
    COST_FUNC_UNIT.short,
]

HEURISTIC_CORNERS: Alias = Alias('heuristic-corners', 'pacai.student.singlesearch.corners_heuristic')
HEURISTIC_EUCLIDEAN: Alias = Alias('heuristic-euclidean', 'pacai.search.distance.euclidean_heuristic')
HEURISTIC_FOOD: Alias = Alias('heuristic-food', 'pacai.student.singlesearch.food_heuristic')
HEURISTIC_MANHATTAN: Alias = Alias('heuristic-manhattan', 'pacai.search.distance.manhattan_heuristic')
HEURISTIC_NULL: Alias = Alias('heuristic-null', 'pacai.search.common.null_heuristic')

HEURISTIC_SHORT_NAMES: list[str] = [
    HEURISTIC_CORNERS.short,
    HEURISTIC_EUCLIDEAN.short,
    HEURISTIC_FOOD.short,
    HEURISTIC_MANHATTAN.short,
    HEURISTIC_NULL.short,
]

SEARCH_PROBLEM_CORNERS: Alias = Alias('search-problem-corners', 'pacai.student.singlesearch.CornersSearchProblem')
SEARCH_PROBLEM_FOOD: Alias = Alias('search-problem-food', 'pacai.search.food.FoodSearchProblem')
SEARCH_PROBLEM_POSITION: Alias = Alias('search-problem-position', 'pacai.search.position.PositionSearchProblem')

SEARCH_PROBLEM_SHORT_NAMES: list[str] = [
    SEARCH_PROBLEM_CORNERS.short,
    SEARCH_PROBLEM_FOOD.short,
    SEARCH_PROBLEM_POSITION.short,
]

SEARCH_SOLVER_ASTAR: Alias = Alias('search-solver-astar', 'pacai.student.singlesearch.astar_search')
SEARCH_SOLVER_BFS: Alias = Alias('search-solver-bfs', 'pacai.student.singlesearch.breadth_first_search')
SEARCH_SOLVER_DFS: Alias = Alias('search-solver-dfs', 'pacai.student.singlesearch.depth_first_search')
SEARCH_SOLVER_MAZE_TINY: Alias = Alias('search-solver-maze-tiny', 'pacai.search.mazetiny.maze_tiny_search')
SEARCH_SOLVER_RANDOM: Alias = Alias('search-solver-random', 'pacai.search.random.random_search')
SEARCH_SOLVER_UCS: Alias = Alias('search-solver-ucs', 'pacai.student.singlesearch.uniform_cost_search')

SEARCH_SOLVER_SHORT_NAMES: list[str] = [
    SEARCH_SOLVER_ASTAR.short,
    SEARCH_SOLVER_BFS.short,
    SEARCH_SOLVER_DFS.short,
    SEARCH_SOLVER_MAZE_TINY.short,
    SEARCH_SOLVER_RANDOM.short,
    SEARCH_SOLVER_UCS.short,
]

STATE_EVAL_BASE: Alias = Alias('state-eval-base', 'pacai.core.gamestate.base_eval')
STATE_EVAL_MINIMAX_BETTER: Alias = Alias('state-eval-minimax-better', 'pacai.student.multiagents.better_state_eval')

STATE_EVAL_SHORT_NAMES: list[str] = [
    STATE_EVAL_BASE.short,
    STATE_EVAL_MINIMAX_BETTER.short,
]

UI_NULL: Alias = Alias('null', 'pacai.ui.null.NullUI')
UI_STDIO: Alias = Alias('text', 'pacai.ui.text.StdioUI', skip_windows_test = True)
UI_RAW_TEXT: Alias = Alias('raw-text', 'pacai.ui.text.TextUI', skip_windows_test = True)
UI_TK: Alias = Alias('tk', 'pacai.ui.tk.TkUI')
UI_WEB: Alias = Alias('web', 'pacai.ui.web.WebUI')

UI_SHORT_NAMES: list[str] = [
    UI_NULL.short,
    UI_STDIO.short,
    UI_TK.short,
    UI_WEB.short,
]

# Misc

MDP_STATE_CLASS_GRIDWORLD: Alias = Alias('mdp-state-class-gridworld', 'pacai.gridworld.mdp.GridWorldMDPState')
