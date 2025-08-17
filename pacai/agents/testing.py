import time
import typing

import pacai.agents.dummy
import pacai.core.action
import pacai.core.gamestate

class TimeoutAgent(pacai.agents.dummy.DummyAgent):
    """
    A testing agent that will wait a specific amount of time before completing specific tasks
    (starting up, getting an action, etc).
    By default the agent will wait no extra time before these action,
    but will use agent arguments to decide how long to wait.
    All wait times are in floating seconds.
    """

    def __init__(self,
            game_start_wait: float = 0.0,
            game_complete_wait: float = 0.0,
            get_action_wait: float = 0.0,
            **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        self._game_start_wait: float = float(game_start_wait)
        """ The amount of time to wait before acknowledging the start of the game. """

        self._game_complete_wait: float = float(game_complete_wait)
        """ The amount of time to wait before acknowledging the completion of the game. """

        self._get_action_wait: float = float(get_action_wait)
        """ The amount of time to wait before returning an action. """

    def game_start(self, initial_state: pacai.core.gamestate.GameState) -> None:
        time.sleep(self._game_start_wait)
        super().game_start(initial_state)

    def game_complete(self, final_state: pacai.core.gamestate.GameState) -> None:
        time.sleep(self._game_complete_wait)
        super().game_complete(final_state)

    def get_action(self, state: pacai.core.gamestate.GameState) -> pacai.core.action.Action:
        time.sleep(self._get_action_wait)
        return super().get_action(state)
