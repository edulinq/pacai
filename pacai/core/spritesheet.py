"""
A sprite sheet is an image that contains images (or "sprites") for different components of the game/board.
In pacai, a sprite sheet is composed of two files: a JSON config and a png/jpg image that contains the actual pixels.

The JSON config is a JSON object that contains the following key/values:
 - filename: str
 - height: int
 - width: int
 - background: Color
 - highlight: Color
 - default: Coordinate
 - markers: dict[pacai.core.board.Marker, MarkerSprites]

`Coordinates` represent locations within the sprite sheet,
it is an array of two integers representing the row and column.
The top left is the origin, and the coordinates already take the height/width into account
(so, [1, 1] has a top left corner at pixel (height, width)).

`Color` is an RGB tuple of int (all between 0 and 255) that represents an RGB color.

Default `background` is [0, 0, 0] (black).
Default `highlight` is [255, 0, 0] (red).
Default `text` is [255, 255, 255] (white).

`MarkerSprites` represent the sprite information for a single marker.
They are JSON objects with the following key/values:
 - default: Coordinate
 - actions: dict[pacai.core.action.Action, list[Coordinate]]
 - adjacency: dict[pacai.core.board.AdjacencyString, Coordinate]

The `actions` value is a JSON object where the keys are actions (pacai.core.action.Action)
and the values are lists of coordinates.
Each coordinate represents one animation frame.
These animation frames can be cycled through to give the graphics some liveliness
(e.g. a pacman moving in the same direction can open and close their mouth).

The `adjacency` object indicates sprites to use when there are objects that are adjacent to the context object.
They are keyed by and pacai.core.board.AdjacencyString and contain a single coordinate as the value
(these do not animate).
This key is typically used for walls so that they can come together in reasonable ways.
When used for walls, a T indicates that there should be an opening in the specified direction.
"""

import os
import typing

import PIL.Image
import edq.util.json

import pacai.core.board

THIS_DIR: str = os.path.join(os.path.dirname(os.path.realpath(__file__)))
SPRITE_SHEETS_DIR: str = os.path.join(THIS_DIR, '..', 'resources', 'spritesheets')

KEY_ACTIONS: str = 'actions'
KEY_ADJACENCY: str = 'adjacency'
KEY_BACKGROUND: str = 'background'
KEY_DEFAULT: str = 'default'
KEY_FILENAME: str = 'filename'
KEY_HEIGHT: str = 'height'
KEY_HIGHLIGHT: str = 'highlight'
KEY_MARKERS: str = 'markers'
KEY_TEXT: str = 'text'
KEY_WIDTH: str = 'width'

DEFAULT_BACKGROUND: tuple[int, int, int] = (0, 0, 0)
DEFAULT_HIGHLIGHT: tuple[int, int, int] = (255, 0, 0)
DEFAULT_TEXT: tuple[int, int, int] = (255, 255, 255)

class SpriteSheet:
    """
    Sprite sheets contain all the graphics for the markers on a board.
    They are typically loaded from JSON files which define
    what each sprite represents.
    """

    def __init__(self,
            height: int, width: int,
            background: tuple[int, int, int],
            highlight: tuple[int, int, int],
            text: tuple[int, int, int],
            default_sprite: PIL.Image.Image | None,
            default_marker_sprites: dict[pacai.core.board.Marker, PIL.Image.Image],
            action_sprites: dict[pacai.core.board.Marker, dict[pacai.core.action.Action, list[PIL.Image.Image]]],
            adjacency_sprites: dict[pacai.core.board.Marker, dict[pacai.core.board.AdjacencyString, PIL.Image.Image]],
            ) -> None:
        self.height: int = height
        """ The height of a sprite. """

        self.width: int = width
        """ The width of a sprite. """

        self.background: tuple[int, int, int] = background
        """ The color (RGB) for the image's background. """

        self.highlight: tuple[int, int, int] = highlight
        """ The color (RGB) for the image's highlight. """

        self.text: tuple[int, int, int] = text
        """ The color (RGB) for the image's text color. """

        self._default_sprite: PIL.Image.Image | None = default_sprite
        """ The fallback sprite to use for the entire sprite sheet. """

        self._default_marker_sprites: dict[pacai.core.board.Marker, PIL.Image.Image] = default_marker_sprites
        """ The fallback sprite to use for each marker. """

        self._action_sprites: dict[pacai.core.board.Marker, dict[pacai.core.action.Action, list[PIL.Image.Image]]] = action_sprites
        """
        Sprites that represent a marker taking a specific action.
        Each list of sprites represents a animation.
        Each animation must have at least one image
        (which visually makes it not an animation,
        but in our terminology an animation is just an ordered list of images).
        """

        self._adjacency_sprites: dict[pacai.core.board.Marker, dict[pacai.core.board.AdjacencyString, PIL.Image.Image]] = adjacency_sprites
        """
        Sprites that represent different versions when there are objects in specific directions.
        """

        self._animation_counts: dict[str, dict[pacai.core.board.Marker, tuple[pacai.core.action.Action, int]]] = {}
        """
        Keep track of the number of times a marker/action pair has been called for,
        so we can keep track of animations.
        The first key is the "animation key" that will allow multiple sources to use the same SpriteSheet
        and still keep their animations separate.
        Note that any action subsequent calls with different actions will reset the count
        (only repeated actions will result in an incrementing count).
        """

    def get_sprite(self,
            marker: pacai.core.board.Marker | None = None,
            action: pacai.core.action.Action | None = None,
            adjacency: pacai.core.board.AdjacencyString | None = None,
            animation_key: str | None = None,
            ) -> PIL.Image.Image:
        """
        Get the sprite for the requested marker/action pair.
        If there is no sprite for that specific pairing, fall back to the default for the marker.
        If the marker has no default, fall back to the sheet's default.
        If the sheet also has no default, raise an error.

        Both `action` and `adjacency` should not be provided,
        but they can both be missing (a default sprite will be returned).

        This method will keep track of animations and return the next animation frame during subsequent calls.
        Each unique `animation_key` will have its own set of tracking of animations.
        This allows different components to share a SpriteSheet without stepping on each others animations.
        A value of None will always result in fetching the first animation frame.
        """

        if ((action is not None) and (adjacency is not None)):
            raise ValueError("Both adjacency and action cannot be non-None.")

        # Start with the default sprite.
        sprite = self._default_sprite

        if (marker is not None):
            # Check for a marker default sprite.
            sprite = self._default_marker_sprites.get(marker, sprite)

            # Check the actions or adjacency for a more specific sprite.
            if (action is not None):
                animation_count = self._next_animation_count(marker, action, animation_key)
                animation_frames = self._action_sprites.get(marker, {}).get(action, [])
                if (len(animation_frames) > 0):
                    sprite = animation_frames[animation_count % len(animation_frames)]
            elif (adjacency is not None):
                # Pull from the adjacency sprites, but fallback to the current sprite.
                sprite = self._adjacency_sprites.get(marker, {}).get(adjacency, sprite)

        if (sprite is None):
            raise ValueError(f"Could not find a matching sprite for action = '{action}', adjacency = '{adjacency}', key = '{animation_key}').")

        return sprite

    def _next_animation_count(self, marker: pacai.core.board.Marker, action: pacai.core.action.Action, animation_key: str | None = None) -> int:
        """
        Get the next animation count for the requested resource,
        and manage the existing count
        (increment for repeated actions, and reset for different actions).
        """

        if (animation_key is None):
            return 0

        if (animation_key not in self._animation_counts):
            self._animation_counts[animation_key] = {}

        animation_keys = self._animation_counts[animation_key]

        if (marker not in animation_keys):
            animation_keys[marker] = (action, -1)

        info = animation_keys[marker]

        # If we got the same action, increment the animation count.
        # If we got a different action, reset the count to zero for this new action.
        if (action == info[0]):
            info = (action, info[1] + 1)
        else:
            info = (action, 0)

        # Update the count.
        animation_keys[marker] = info

        return info[1]

    def clear_animation_counts(self, animation_key: str | None = None) -> None:
        """
        Clear the animation counts (position of the animation) for the given key,
        or all counts if no key is provided.
        """

        if (animation_key is None):
            self._animation_counts = {}
        else:
            self._animation_counts[animation_key] = {}

    def position_to_pixels(self, position: pacai.core.board.Position) -> tuple[int, int]:
        """ Get the pixels (x, y) for this position. """

        return (position.col * self.width, position.row * self.height)

def load(path: str) -> SpriteSheet:
    """
    Load a sprite sheet from a file.
    If the given path does not exist,
    try to prefix the path with the standard sprite sheet directory and suffix with the standard extension.
    """

    raw_path = path

    # If the path does not exist, try the sprite sheets directory.
    if (not os.path.exists(path)):
        path = os.path.join(SPRITE_SHEETS_DIR, path)

        # If this path does not have a good extension, add one.
        if (os.path.splitext(path)[-1] != '.json'):
            path = path + '.json'

    if (not os.path.exists(path)):
        raise ValueError(f"Could not find sprite sheet, path does not exist: '{raw_path}'.")

    try:
        return _load(path)
    except Exception as ex:
        raise ValueError(f"Error loading sprite sheet config: '{path}'.") from ex

def _load(config_path: str) -> SpriteSheet:
    config = edq.util.json.load_path(config_path)
    height, width, sprites = _load_sprites(config, config_path)

    background: tuple[int, int, int] = _parse_color(config, KEY_BACKGROUND, DEFAULT_BACKGROUND)
    highlight: tuple[int, int, int] = _parse_color(config, KEY_HIGHLIGHT, DEFAULT_HIGHLIGHT)
    text: tuple[int, int, int] = _parse_color(config, KEY_TEXT, DEFAULT_TEXT)

    default_sprite: PIL.Image.Image | None = None
    default_marker_sprites: dict[pacai.core.board.Marker, PIL.Image.Image] = {}
    action_sprites: dict[pacai.core.board.Marker, dict[pacai.core.action.Action, list[PIL.Image.Image]]] = {}
    adjacency_sprites: dict[pacai.core.board.Marker, dict[pacai.core.board.AdjacencyString, PIL.Image.Image]] = {}

    default_coordinate = config.get(KEY_DEFAULT, None)
    if (default_coordinate is not None):
        default_sprite = _fetch_coordinate(sprites, default_coordinate)

    for (marker, marker_sprites) in config.get(KEY_MARKERS, {}).items():
        default, action, adjacency = _fetch_marker_sprites(sprites, marker_sprites)

        if (default is not None):
            default_marker_sprites[marker] = default

        if (len(action) > 0):
            action_sprites[marker] = action

        if (len(adjacency) > 0):
            adjacency_sprites[marker] = adjacency

    return SpriteSheet(height, width, background, highlight, text, default_sprite, default_marker_sprites, action_sprites, adjacency_sprites)

def _fetch_marker_sprites(
            sprites: list[list[PIL.Image.Image]],
            marker_sprites: dict[str, typing.Any]
            ) -> tuple[
                PIL.Image.Image | None,
                dict[pacai.core.action.Action, list[PIL.Image.Image]],
                dict[pacai.core.board.AdjacencyString, PIL.Image.Image]]:
    default_sprite: PIL.Image.Image | None = None
    action_sprites: dict[pacai.core.action.Action, list[PIL.Image.Image]] = {}
    adjacency_sprites: dict[pacai.core.board.AdjacencyString, PIL.Image.Image] = {}

    default_coordinate = marker_sprites.get(KEY_DEFAULT, None)
    if (default_coordinate is not None):
        default_sprite = _fetch_coordinate(sprites, default_coordinate)

    for (action, coordinates) in marker_sprites.get(KEY_ACTIONS, {}).items():
        if (len(coordinates) == 0):
            continue

        action_sprites[action] = []
        for coordinate in coordinates:
            action_sprites[action].append(_fetch_coordinate(sprites, coordinate))

    for (adjacency, coordinate) in marker_sprites.get(KEY_ADJACENCY, {}).items():
        adjacency_sprites[adjacency] = _fetch_coordinate(sprites, coordinate)

    return (default_sprite, action_sprites, adjacency_sprites)

def _fetch_coordinate(sprites: list[list[PIL.Image.Image]], raw_coordinate: typing.Any) -> PIL.Image.Image:
    (row, col) = _parse_coordinate(raw_coordinate)
    return sprites[row][col]

def _parse_color(config: dict[str, typing.Any], key: str, default: tuple[int, int, int]) -> tuple[int, int, int]:
    if (key not in config):
        return default

    color = config.get(key)
    if ((not isinstance(color, list)) or (len(color) != 3)):
        raise ValueError(f"Color must be a list of three ints, found: '{str(color)}'.")

    color = (
        _parse_int(color[0]),
        _parse_int(color[1]),
        _parse_int(color[2]),
    )

    for (i, component) in enumerate(color):
        if ((component < 0) or (component > 255)):
            raise ValueError(f"Color component {i} is out of bounds, must be between 0 and 255. Found: '{color}'.")

    return color

def _parse_coordinate(raw_coordinate: typing.Any) -> tuple[int, int]:
    if (not isinstance(raw_coordinate, list)):
        raise ValueError(f"Coordinate is not a list/array: '{str(raw_coordinate)}'.")

    if (len(raw_coordinate) != 2):
        raise ValueError(f"Did not find exactly two items in a coordinate, found {len(raw_coordinate)}.")

    row = _parse_int(raw_coordinate[0])
    col = _parse_int(raw_coordinate[1])

    return (row, col)

def _load_sprites(config: dict[str, typing.Any], config_path: str) -> tuple[int, int, list[list[PIL.Image.Image]]]:
    path = str(config.get(KEY_FILENAME, '')).strip()
    if (len(path) == 0):
        raise ValueError(f"Invalid or missing '{KEY_FILENAME}' field.")

    # If the path is not absolute, make it relative to the config path.
    if (not os.path.isabs(path)):
        path = os.path.join(os.path.dirname(config_path), path)

    try:
        height = _parse_int(config.get(KEY_HEIGHT))
    except Exception as ex:
        raise ValueError(f"Invalid or missing '{KEY_HEIGHT}' field.") from ex

    try:
        width = _parse_int(config.get(KEY_WIDTH))
    except Exception as ex:
        raise ValueError(f"Invalid or missing '{KEY_WIDTH}' field.") from ex

    raw_sheet = PIL.Image.open(path)

    if (raw_sheet.height % height != 0):
        raise ValueError(f"Sprite sheet height ({raw_sheet.height}) is not a multiple of the sprite height ({height}).")

    if (raw_sheet.width % width != 0):
        raise ValueError(f"Sprite sheet width ({raw_sheet.width}) is not a multiple of the sprite width ({width}).")

    sprites: list[list[PIL.Image.Image]] = []

    for row in range(raw_sheet.height // height):
        sprites.append([])

        for col in range(raw_sheet.width // width):
            sprites[row].append(_crop(raw_sheet, row, col, height, width))

    return height, width, sprites

def _parse_int(raw_value:  typing.Any) -> int:
    if (isinstance(raw_value, int)):
        return raw_value

    if (isinstance(raw_value, float)):
        return int(raw_value)

    return int(str(raw_value))

def _crop(source: PIL.Image.Image, row: int, col: int, height: int, width: int) -> PIL.Image.Image:
    # (left, upper, right, lower)
    rectangle = (
        col * width,
        row * height,
        (col + 1) * width,
        (row + 1) * height,
    )

    return source.crop(rectangle)
