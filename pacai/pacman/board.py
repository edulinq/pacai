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
