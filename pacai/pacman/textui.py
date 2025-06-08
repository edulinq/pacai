import typing

import pacai.core.board
import pacai.core.gamestate
import pacai.pacman.board
import pacai.pacman.gamestate
import pacai.ui.text

MARKER_OVERRIDES: dict[pacai.core.board.Marker, str] = {
    pacai.core.board.MARKER_WALL: '█',
    pacai.pacman.board.MARKER_PELLET: '∙',
    pacai.pacman.board.MARKER_CAPSULE: '⦾',
    pacai.core.board.MARKER_AGENT_0: 'X',
}

class StdioUI(pacai.ui.text.StdioUI):
    """ A text-based UI specifically for pacman. """

    def _translate_marker(self, marker: pacai.core.board.Marker, state: pacai.core.gamestate.GameState) -> str:
        # Make some of the markers more visually clear.
        state = typing.cast(pacai.pacman.gamestate.GameState, state)

        if (marker.is_agent()):
            # Note that pacman has already been checked for.
            if (state.scared_timers.get(marker.get_agent_index(), 0) > 0):
                # The ghost is scared.
                return 'ᗢ'

            return 'ᗣ'

        return MARKER_OVERRIDES.get(marker, str(marker))
