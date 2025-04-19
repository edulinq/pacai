import pacai.core.board
import pacai.core.gamestate
import pacai.core.ui

class Text(pacai.core.ui.UI):
    """
    A simple UI that renders the game to stdout.
    This UI will be simple and generally meant for debugging.
    """

    def update(self, state: pacai.core.gamestate.GameState) -> None:
        grid = state.board.to_grid()
        for row in grid:
            line = ''.join([self._translate_marker(marker, state) for marker in row])
            print(line)

        print(f"Score: {state.score}")

        if (state.game_over):
            print('Game Over!')

        print('', flush = True)

    def game_start(self, initial_state: pacai.core.gamestate.GameState) -> None:
        self.update(initial_state)

    def game_complete(self, final_state: pacai.core.gamestate.GameState) -> None:
        self.update(final_state)

    def close(self) -> None:
        pass

    def _translate_marker(self, marker: pacai.core.board.Marker, state: pacai.core.gamestate.GameState) -> str:
        """
        Convert a marker to a string.
        This is generally trivial (since a marker is already a string),
        but this allows children to implement special conversions.
        """

        return marker
