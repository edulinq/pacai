import random

import pacai.core.action
import pacai.core.agent
import pacai.core.gamestate

class RandomAgent(pacai.core.agent.Agent):
    """ An agent that just takes random (legal) action. """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, *kwargs)

        self._rng: random.Random | None = None

    def get_action(self, state: pacai.core.gamestate.GameState, user_inputs: list[pacai.core.action.Action]) -> pacai.core.action.Action:
        """ Choose a random action. """

        if (self._rng is None):
            raise ValueError("Cannot get an action before starting the game.")

        legal_actions = state.get_legal_actions()
        return self._rng.choice(legal_actions)

    def game_start(self, agent_index: int, suggested_seed: int, initial_state: pacai.core.gamestate.GameState) -> None:
        """ Initialize the agent's random number generator. """

        self._rng = random.Random(suggested_seed)

    def game_complete(self, final_state: pacai.core.gamestate.GameState) -> None:
        """ Do nothing. """

        pass
