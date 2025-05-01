import pacai.core.board

MARKER_PELLET: pacai.core.board.Marker = pacai.core.board.Marker('.')
MARKER_CAPSULE: pacai.core.board.Marker = pacai.core.board.Marker('o')

class Board(pacai.core.board.Board):
    """
    A board for Pacman.

    In addition to walls, Pacman boards also have:
    pellets ('.')
    and capsules ('o').
    """

    def __init__(self, *args, additional_markers: list[str] = [], **kwargs) -> None:
        additional_markers += [
            MARKER_PELLET,
            MARKER_CAPSULE,
        ]

        super().__init__(*args, additional_markers = additional_markers, **kwargs)  # type: ignore
