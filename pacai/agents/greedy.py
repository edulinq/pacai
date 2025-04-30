import pacai.core.action
import pacai.core.agent
import pacai.core.agentinfo
import pacai.core.gamestate
import pacai.util.reflection

EVAL_FUNC_KEY: str = 'eval_func'
""" The key for the evaluation function inside the agent info's extra arguments. """

DEFAULT_EVAL_FUNC_REF: pacai.util.reflection.Reference = pacai.util.reflection.Reference('pacai.core.agent.base_eval')
""" The default evaluation function to use. """

class GreedyAgent(pacai.core.agent.Agent):
    """
    An agent that greedily takes the available move with the best score at the time.
    If multiple moves have the same score, this agent will just randomly choose between them.
    """

    def __init__(self, agent_info: pacai.core.agentinfo.AgentInfo, *args, **kwargs) -> None:
        super().__init__(agent_info, *args, **kwargs)

        eval_func_name = agent_info.extra_arguments.get(EVAL_FUNC_KEY, DEFAULT_EVAL_FUNC_REF)
        eval_func_object = pacai.util.reflection.fetch(eval_func_name)
        if (not isinstance(eval_func_object, pacai.core.agent.EvaluationFunction)):
            raise ValueError(f"Evaluation function '{eval_func_name}' is not a pacai.core.agent.EvaluationFunction.")

        self._evaluation_function: pacai.core.agent.EvaluationFunction = eval_func_object
        """ The evaluation function that agent will use to assess game states. """

    def get_action(self, state: pacai.core.gamestate.GameState, user_inputs: list[pacai.core.action.Action]) -> pacai.core.action.Action:
        legal_actions = state.get_legal_actions()
        if (len(legal_actions) == 1):
            return legal_actions[0]

        # Don't consider stopping unless we can do nothing else.
        if (pacai.core.action.STOP in legal_actions):
            legal_actions.remove(pacai.core.action.STOP)

        successors = [(state.generate_sucessor(action), action) for action in legal_actions]
        scores = [(self._evaluation_function(successor), action) for (successor, action) in successors]

        best_score = max(scores)[0]
        best_actions = [pair[1] for pair in scores if pair[0] == best_score]

        return self._rng.choice(best_actions)
