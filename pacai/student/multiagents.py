import typing

import pacai.agents.greedy
import pacai.agents.minimax
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

    def __init__(self, **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        # Put code here if you want.

    def evaluate_state(self,
            state: pacai.core.gamestate.GameState,
            action: pacai.core.action.Action | None = None,
            **kwargs: typing.Any) -> float:
        # This would be a great place to improve your reflex agent.
        return super().evaluate_state(state, action)

class MyMinimaxLikeAgent(pacai.agents.minimax.MinimaxLikeAgent):
    """
    An agent that implements all the required methods for the minimax family of algorithms.
    Default implementations are supplied, so the agent should run right away,
    but it will not be very good.

    To implement minimax, minimax_step_max() and minimax_step_min() are required
    (you can ignore alpha and beta).

    To implement minimax with alpha-beta pruning,
    minimax_step_max() and minimax_step_min() with alpha and beta are required.

    To implement expectimax, minimax_step_max() and minimax_step_expected_min() are required.

    You are free to implement/override any methods you need to.
    """

    def __init__(self, **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        # You can use the constructor if you need to.

    def minimax_step_max(self,
            state: pacai.core.gamestate.GameState,
            ply_count: int,
            legal_actions: list[pacai.core.action.Action],
            alpha: float,
            beta: float,
            ) -> tuple[list[pacai.core.action.Action], float]:
        # *** Your Code Here ***
        return super().minimax_step_max(state, ply_count, legal_actions, alpha, beta)

    def minimax_step_min(self,
            state: pacai.core.gamestate.GameState,
            ply_count: int,
            legal_actions: list[pacai.core.action.Action],
            alpha: float,
            beta: float,
            ) -> tuple[list[pacai.core.action.Action], float]:
        # *** Your Code Here ***
        return super().minimax_step_min(state, ply_count, legal_actions, alpha, beta)

    def minimax_step_expected_min(self,
            state: pacai.core.gamestate.GameState,
            ply_count: int,
            legal_actions: list[pacai.core.action.Action],
            alpha: float,
            beta: float,
            ) -> float:
        # *** Your Code Here ***
        return super().minimax_step_expected_min(state, ply_count, legal_actions, alpha, beta)

def better_state_eval(
        state: pacai.core.gamestate.GameState,
        agent: typing.Any | None = None,
        action: pacai.core.action.Action | None = None,
        **kwargs: typing.Any) -> float:
    """
    Create a better state evaluation function for your MyMinimaxLikeAgent agent!

    In this comment, include a description of what you are doing.

    *** Your Text Here ***
    """

    # *** Your Code Here ***
    return state.score
