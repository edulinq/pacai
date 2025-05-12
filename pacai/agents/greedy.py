import pacai.core.action
import pacai.core.agent
import pacai.core.gamestate
import pacai.util.alias
import pacai.util.reflection

class GreedyAgent(pacai.core.agent.Agent):
    """
    An agent that greedily takes the available move with the best score at the time.
    If multiple moves have the same score, this agent will just randomly choose between them.
    """

    def __init__(self,
            eval_func: pacai.core.gamestate.EvaluationFunction | pacai.util.reflection.Reference | str = pacai.util.alias.STATE_EVAL_BASE.long,
            **kwargs) -> None:
        super().__init__(**kwargs)

        clean_eval_func = pacai.util.reflection.resolve_and_fetch(pacai.core.gamestate.EvaluationFunction, eval_func)
        self._evaluation_function: pacai.core.gamestate.EvaluationFunction = clean_eval_func
        """ The evaluation function that agent will use to assess game states. """

    def get_action(self, state: pacai.core.gamestate.GameState) -> pacai.core.action.Action:
        legal_actions = state.get_legal_actions()
        if (len(legal_actions) == 1):
            return legal_actions[0]

        # Don't consider stopping unless we can do nothing else.
        if (pacai.core.action.STOP in legal_actions):
            legal_actions.remove(pacai.core.action.STOP)

        successors = [(state.generate_sucessor(action), action) for action in legal_actions]
        scores = [(self.evaluate_state(successor, action, state), action) for (successor, action) in successors]

        best_score = max(scores)[0]
        best_actions = [pair[1] for pair in scores if pair[0] == best_score]

        return self._rng.choice(best_actions)

    def evaluate_state(self,
            state: pacai.core.gamestate.GameState,
            action: pacai.core.action.Action,
            old_state: pacai.core.gamestate.GameState,
            ) -> float:
        """
        Evaluate the state to get a decide how good an action was.
        The base implementation for this function just calls `self._evaluation_function`,
        but child classes may override this method to easily implement their own evaluations.
        """

        return self._evaluation_function(state, action = action, old_state = old_state)
