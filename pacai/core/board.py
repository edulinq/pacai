import os
import re

import pacai.util.file
import pacai.util.json
import pacai.util.reflection

THIS_DIR: str = os.path.join(os.path.dirname(os.path.realpath(__file__)))
BOARDS_DIR: str = os.path.join(THIS_DIR, '..', 'boards')

SEPARATOR_PATTERN: re.Pattern = re.compile(r'^\s*-{3,}\s*$')

DEFAULT_BOARD_CLASS = 'pacai.core.board.Board'

class Board:
    """
    A board represents the static (non-agent) components of a game.
    For example, a board contains the walls and collectable items.

    Most types of games (anything that would subclass pacai.core.game.Game) should probably
    also subclass this to make their own type of board.

    On disk, boards are represented in files that have two sections (divided by a '---' line).
    The first section is a JSON object that holds any options for the board.
    The second section is a textual representation of the board.
    The specific board class (usually specified by the board options) should know how to interpret the text-based board.
    """

    def __init__(self, marker_wall = '%', **kwargs) -> None:
        # TEST
        pass

def load_path(path: str) -> Board:
    """ Load a board from a file. """

    text = pacai.util.file.read(path, strip = False)
    return load_string(text)

def load_string(text: str) -> Board:
    """ Load a board from a string. """

    separator_index = -1
    lines = text.split("\n")

    for i in range(len(lines)):
        if (SEPARATOR_PATTERN.match(lines[i])):
            separator_index = i
            break

    if (separator_index == -1):
        # No separator was found.
        options_text = ''
        board_text = "\n".join(lines)
    else:
        options_text = "\n".join(lines[:i])
        board_text = "\n".join(lines[(i + 1):])

    options_text = options_text.strip()
    if (len(options_text) == 0):
        options = {}
    else:
        options = pacai.util.json.loads(options_text)

    board_class = options.get('class', DEFAULT_BOARD_CLASS)
    return pacai.util.reflection.new_object(board_class, **options)
