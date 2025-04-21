import pacai.core.gamestate
import pacai.core.ui

class NullUI(pacai.core.ui.UI):
    """
    A UI that renders nothing.
    This is useful when are more interested in the output of the game
    (e.g., the log or gif) than seeing the actual game.
    """

    def draw(self, state: pacai.core.gamestate.GameState) -> None:
        pass

    def wait_for_fps(self) -> None:
        pass
