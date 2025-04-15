import pacai.core.board

MARKER_PELLET: pacai.core.board.Marker = pacai.core.board.Marker('.')
MARKER_CAPSULE: pacai.core.board.Marker = pacai.core.board.Marker('o')
MARKER_GHOST: pacai.core.board.Marker = pacai.core.board.Marker('G')
MARKER_PACMAN: pacai.core.board.Marker = pacai.core.board.Marker('P')

class Board(pacai.core.board.Board):
    """
    A board for Pacman.

    In addition to walls, Pacman boards also have:
    pellets ('.'),
    capsules ('o'),
    ghosts ('G'),
    and Pacman ('P').
    """

    def __init__(self, board_text: str, extra_markers: list[str] = [], **kwargs) -> None:
        extra_markers += [
            MARKER_PELLET,
            MARKER_CAPSULE,
            MARKER_GHOST,
            MARKER_PACMAN,
        ]

        super().__init__(board_text, extra_markers = extra_markers, **kwargs)

        # TODO(eriq): Verify that the ghost indexes match.

        self._agents: list[int | None] = [None]
        """
        Keep explicit track of each agent on this board.
        The agents are indexed by their same index in the game.
        Pacman is always 0 and the ghosts are indexed by the order they appear.

        A None position means that the agent is not currently on the board.

        Note that this quick lookup requires additional maintenance when agents move.
        """

        for index in range(len(self._locations)):
            marker = self._locations[index]
            if (marker not in {MARKER_PACMAN, MARKER_GHOST}):
                continue

            if (marker == MARKER_PACMAN):
                self._agents[0] = index
            else:
                self._agents.append(index)

    def get_agent_position(self, agent_index: int) -> pacai.core.board.Position | None:
        index = self._agents[agent_index]
        if (index is None):
            return None

        return pacai.core.board.Position.from_index(index, self.width)
