"""
The main executable for running a game of Capture.
"""

import argparse
import sys
import typing

import pacai.capture.game
import pacai.util.bin

DEFAULT_BOARD: str = 'capture-medium'
DEFAULT_SPRITE_SHEET: str = 'pacman'

def get_additional_ui_options(args: argparse.Namespace) -> dict[str, typing.Any]:
    """ Get additional options for the UI. """

    return {
        'sprite_sheet_path': DEFAULT_SPRITE_SHEET,
    }

def main() -> int:
    """ Invoke a game of Capture. """

    return pacai.util.bin.run_main(
        description = "Play a game of Capture.",
        default_board = DEFAULT_BOARD,
        game_class = pacai.capture.game.Game,
        get_additional_ui_options = get_additional_ui_options,
    )

if (__name__ == '__main__'):
    sys.exit(main())
