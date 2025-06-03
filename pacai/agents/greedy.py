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

    def get_action(self, state: pacai.core.gamestate.GameState) -> pacai.core.action.Action:
        legal_actions = state.get_legal_actions()
        if (len(legal_actions) == 1):
            return legal_actions[0]

        # Don't consider stopping unless we can do nothing else.
        if (pacai.core.action.STOP in legal_actions):
            legal_actions.remove(pacai.core.action.STOP)

        successors = [(state.generate_successor(action, self.rng), action) for action in legal_actions]
        scores = [(self.evaluate_state(successor, action = action), action) for (successor, action) in successors]

        best_score = max(scores)[0]
        best_actions = [pair[1] for pair in scores if pair[0] == best_score]

        return self.rng.choice(best_actions)
