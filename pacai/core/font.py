import enum
import os
import typing

import pacai.core.board

THIS_DIR: str = os.path.join(os.path.dirname(os.path.realpath(__file__)))
DEFAULT_FONT_PATH: str = os.path.join(THIS_DIR, '..', 'resources', 'fonts', 'fragment', 'FragmentMono-Regular.ttf')

class FontSize(enum.Enum):
    """ The allowed size categories for fonts drawn on the board. """

    TINY = 0.10
    SMALL = 0.25
    MEDIUM = 0.50
    LARGE = 0.75

class TextVerticalAlign(enum.Enum):
    """ Vertical alignment for text drawn on the board. """

    TOP = 0.10
    MIDDLE = 0.50
    BOTTOM = 0.90

class TextHorizontalAlign(enum.Enum):
    """ Horizontal alignment for text drawn on the board. """

    LEFT = 0.05
    CENTER = 0.50
    RIGHT = 0.95

DEFAULT_VERTICAL_ANCHORS: dict[TextVerticalAlign, str] = {
    TextVerticalAlign.TOP: 't',
    TextVerticalAlign.MIDDLE: 'm',
    TextVerticalAlign.BOTTOM: 'b',
}

DEFAULT_HORIZONTAL_ANCHORS: dict[TextHorizontalAlign, str] = {
    TextHorizontalAlign.LEFT: 'l',
    TextHorizontalAlign.CENTER: 'm',
    TextHorizontalAlign.RIGHT: 'r',
}

class Text:
    """
    A representation of text.
    """

    def __init__(self,
            text: str,
            size: FontSize = FontSize.MEDIUM,
            vertical_align: TextVerticalAlign = TextVerticalAlign.MIDDLE,
            horizontal_align: TextHorizontalAlign = TextHorizontalAlign.CENTER,
            anchor: str | None = None,
            color: tuple[int, int, int] | None = None,
            ) -> None:
        self.text: str = text
        """ The text to display. """

        self.size: FontSize = size
        """ The size to display the text. """

        self.vertical_align: TextVerticalAlign = vertical_align
        """ The vertical alignment of text. """

        self.horizontal_align: TextHorizontalAlign = horizontal_align
        """ The horizontal alignment of text. """

        if (anchor is None):
            anchor = DEFAULT_HORIZONTAL_ANCHORS[horizontal_align] + DEFAULT_VERTICAL_ANCHORS[vertical_align]

        self.anchor: str = anchor
        """
        The alignment anchor of the text.
        See: https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html#text-anchors .
        """

        self.color: tuple[int, int, int] | None = color
        """ The color of the text. """

class BoardText(Text):
    """
    A representation of text that will appear on the board.
    """

    def __init__(self,
            position: pacai.core.board.Position,
            text: str,
            **kwargs: typing.Any) -> None:
        super().__init__(text, **kwargs)

        self.position: pacai.core.board.Position = position
        """ The position to display the text. """
