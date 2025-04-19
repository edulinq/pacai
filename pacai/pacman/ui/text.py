import typing

import pacai.core.board
import pacai.core.gamestate
import pacai.pacman.board
import pacai.pacman.gamestate
import pacai.ui.text

class Text(pacai.ui.text.Text):
    """ A text-based UI specifically for pacman. """

    def _translate_marker(self, marker: pacai.core.board.Marker, state: pacai.core.gamestate.GameState) -> str:
        # Make some of the markers more visually clear.
        state = typing.cast(pacai.pacman.gamestate.GameState, state)

        if (marker == pacai.core.board.MARKER_WALL):
            return '█'
        elif (marker == pacai.pacman.board.MARKER_PELLET):
            return '∙'
        elif (marker == pacai.pacman.board.MARKER_CAPSULE):
            return '⦾'
        elif (marker == pacai.core.board.MARKER_AGENT_0):
            return 'X'
        elif (marker.is_agent()):
            # Note that pacman has already been checked for.
            if (state.power_time > 0):
                # The ghost is scarred.
                return 'ᗢ'

            return 'ᗣ'
        else:
            return marker
