import typing

import pacai.core.board

MARKER_PELLET: pacai.core.board.Marker = pacai.core.board.Marker('.')
""" Marker for pellets/food. """

MARKER_CAPSULE: pacai.core.board.Marker = pacai.core.board.Marker('o')
""" Marker for power capsules. """

MARKER_SCARED_GHOST: pacai.core.board.Marker = pacai.core.board.Marker('!')
""" A special marker for scared ghosts. """

class Board(pacai.core.board.Board):
    """
    A board for Pacman.

    In addition to walls, Pacman boards also have:
    pellets ('.')
    and capsules ('o').
    """

    def __init__(self, *args: typing.Any, additional_markers: list[str] | None = None, **kwargs: typing.Any) -> None:
        if (additional_markers is None):
            additional_markers = []

        additional_markers += [
            MARKER_PELLET,
            MARKER_CAPSULE,
        ]

        super().__init__(*args, additional_markers = additional_markers, **kwargs)  # type: ignore
