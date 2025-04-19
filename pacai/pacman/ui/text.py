import pacai.core.board
import pacai.core.gamestate
import pacai.ui.text

class Text(pacai.ui.text.Text):
    """ A text-based UI specifically for pacman. """

    def _translate_marker(self, marker: pacai.core.board.Marker, state: pacai.core.gamestate.GameState) -> str:
        return marker
