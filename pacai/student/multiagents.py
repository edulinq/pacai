import pacai.agents.greedy
import pacai.core.action
import pacai.core.gamestate

class ReflexAgent(pacai.agents.greedy.GreedyAgent):
    """
    A simple agent based on pacai.agents.greedy.GreedyAgent.

    You job is to make this agent better (it is pretty bad right now).
    You can change whatever you want about it,
    but it should still be a child of pacai.agents.greedy.GreedyAgent
    and be a "reflex" agent.
    This means that it shouldn't do any formal planning or searching,
    instead it should just look at the state of the game and try to make a good choice in the moment.
    You can make a great agent just by implementing a custom evaluate_state() method
    (and maybe add to the constructor if you want).
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # *** Your Code Here ***

    def evaluate_state(self,
            state: pacai.core.gamestate.GameState,
            action: pacai.core.action.Action | None = None,
            old_state: pacai.core.gamestate.GameState | None = None,
            **kwargs) -> float:
        # *** Your Code Here ***

        # By default, we will just call the parent's method.
        return super().evaluate_state(state, action, old_state)
