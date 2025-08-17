import abc
import argparse
import os
import time
import typing

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import edq.util.time

import pacai.core.action
import pacai.core.board
import pacai.core.font
import pacai.core.gamestate
import pacai.core.spritesheet
import pacai.util.alias
import pacai.util.reflection

DEFAULT_FPS: int = 15

DEFAULT_ANIMATION_FPS: int = 15
DEFAULT_ANIMATION_SKIP_FRAMES: int = 1
MIN_ANIMATION_FPS: int = 1
DEFAULT_ANIMATION_OPTIMIZE: bool = False

DEFAULT_SPRITE_SHEET: str = 'generic'

ANIMATION_KEY: str = 'UI.draw_image'

ANIMATION_EXTS: list[str] = ['.gif', '.webp']
""" The allowed extensions for animation files. """

WASD_CHAR_MAPPING: dict[str, pacai.core.action.Action] = {
    'w': pacai.core.action.NORTH,
    'W': pacai.core.action.NORTH,
    'ArrowUp': pacai.core.action.NORTH,

    'a': pacai.core.action.WEST,
    'A': pacai.core.action.WEST,
    'ArrowLeft': pacai.core.action.WEST,

    's': pacai.core.action.SOUTH,
    'S': pacai.core.action.SOUTH,
    'ArrowDown': pacai.core.action.SOUTH,

    'd': pacai.core.action.EAST,
    'D': pacai.core.action.EAST,
    'ArrowRight': pacai.core.action.EAST,

    ' ': pacai.core.action.STOP,
    'space': pacai.core.action.STOP,
    'Space': pacai.core.action.STOP,
    'SPACE': pacai.core.action.STOP,
}
""" A character to action mapping using the common WASD scheme. """

ARROW_CHAR_MAPPING: dict[str, pacai.core.action.Action] = {
    'Up': pacai.core.action.NORTH,
    'ArrowUp': pacai.core.action.NORTH,

    'Left': pacai.core.action.WEST,
    'ArrowLeft': pacai.core.action.WEST,

    'Down': pacai.core.action.SOUTH,
    'ArrowDown': pacai.core.action.SOUTH,

    'Right': pacai.core.action.EAST,
    'ArrowRight': pacai.core.action.EAST,

    ' ': pacai.core.action.STOP,
    'space': pacai.core.action.STOP,
    'Space': pacai.core.action.STOP,
    'SPACE': pacai.core.action.STOP,
}
""" A character to action mapping using the arrow keys. """

DUAL_CHAR_MAPPING: dict[str, pacai.core.action.Action] = WASD_CHAR_MAPPING | ARROW_CHAR_MAPPING
""" A character to action mapping that uses both WASD_CHAR_MAPPING and ARROW_CHAR_MAPPING. """

class UserInputDevice(abc.ABC):
    """
    This class provides a way for users to convey inputs through a UI.
    Not all UIs will support user input.
    """

    @abc.abstractmethod
    def get_inputs(self) -> list[pacai.core.action.Action]:
        """
        Get any inputs that have occurred since the last call to this method.
        This method is responsible for not returning the same input instance in subsequent calls.
        The last input in the returned list should be the most recent input.
        """

    def close(self) -> None:
        """ Close the user input channel and release all owned resources. """

class UI(abc.ABC):
    """
    UIs represent the basic way that a game interacts with the user,
    by displaying the state of the game and taking input from the user (if applicable).
    """

    def __init__(self,
            user_input_device: UserInputDevice | None = None,
            fps: int = DEFAULT_FPS,
            animation_path: str | None = None,
            animation_optimize: bool = DEFAULT_ANIMATION_OPTIMIZE,
            animation_fps: int = DEFAULT_ANIMATION_FPS,
            animation_skip_frames: int = DEFAULT_ANIMATION_SKIP_FRAMES,
            sprite_sheet_path: str = DEFAULT_SPRITE_SHEET,
            font_path: str = pacai.core.font.DEFAULT_FONT_PATH,
            **kwargs: typing.Any) -> None:
        self._user_input_device: UserInputDevice | None = user_input_device
        """ The device to use to get user input. """

        self._fps: int = fps
        """
        The desired frames per second this game will be displayed at.
        Zero or lower values will be ignored.
        This is just a suggestion that the game will try an accommodate.
        Not all UIs will observe fps.
        """

        self._last_fps_wait: edq.util.time.Timestamp | None = None
        """
        Keep track of the last time the UI waited to adjust the fps.
        We need this information to compute the next wait time.
        """

        self._update_count: int = 0
        """ Keep track of the number of times update() has been called. """

        self._animation_path: str | None = animation_path
        """ If specified, create a animation and write it to this location after the game completes. """

        if (self._animation_path is not None):
            if (os.path.splitext(self._animation_path)[-1] not in ANIMATION_EXTS):
                raise ValueError(f"Animation path must have one of the following extensions {ANIMATION_EXTS}, found '{self._animation_path}'.")

        self._animation_optimize: bool = animation_optimize
        """ Optimize the animation output to reduce file size. """

        self._animation_fps: int = max(MIN_ANIMATION_FPS, animation_fps)
        """ The frame rate for the animation. """

        self._animation_skip_frames: int = max(1, animation_skip_frames)
        """
        Skip this many frames between drawing animation frames.
        This can help speed up animation creation by leaving out less important frames.
        For example, this can be set to the number of agents to only draw frames after all agents have moved.
        """

        self._animation_frames: list[PIL.Image.Image] = []
        """ The frames for the animation (one per call to update(). """

        self._static_base_image: PIL.Image.Image | None = None
        """
        Cache an image that has all of the static (non-changing) elements (like walls) drawn.
        This can be reused as the base image every time we draw an image.
        """

        # Only load sprites (and fonts) if we need them.
        sprite_sheet = None
        fonts = {}
        if (self.requires_sprites() or (self._animation_path is not None)):
            sprite_sheet = pacai.core.spritesheet.load(sprite_sheet_path)

            for font_size in pacai.core.font.FontSize:
                fonts[font_size] = PIL.ImageFont.truetype(font_path, int(sprite_sheet.height * font_size.value))

        self._sprite_sheet: pacai.core.spritesheet.SpriteSheet | None = sprite_sheet
        """ The sprite sheet to use for this UI. """

        self._fonts: dict[pacai.core.font.FontSize, PIL.ImageFont.FreeTypeFont] = fonts
        """ The available fonts indexed by size. """

        self._image_cache: dict[int, PIL.Image.Image] = {}
        """ Cache images (by game state turn count) to avoid redrawing images. """

        self._highlights: dict[pacai.core.board.Position, float] = {}
        """ The current set of board highlights. """

    def update(self,
            state: pacai.core.gamestate.GameState,
            force_draw_image: bool = False,
            board_highlights: list[pacai.core.board.Highlight] | None = None,
            ) -> None:
        """
        Update the UI with the current state of the game.
        This is the main entry point for the game into the UI.
        """

        self.wait_for_fps()

        if (board_highlights is None):
            board_highlights = []

        for board_highlight in board_highlights:
            intensity = board_highlight.get_float_intensity()
            if (intensity is None):
                self._highlights.pop(board_highlight.position, None)
            else:
                self._highlights[board_highlight.position] = intensity

        if ((self._animation_path is not None) and (force_draw_image or (self._update_count % self._animation_skip_frames == 0))):
            image = self.draw_image(state)
            self._animation_frames.append(image)

        self.draw(state)

        self._update_count += 1

    def game_start(self,
            initial_state: pacai.core.gamestate.GameState,
            board_highlights: list[pacai.core.board.Highlight] | None = None,
            ) -> None:
        """ Initialize the UI with the game's initial state. """

        self.update(initial_state, board_highlights = board_highlights, force_draw_image = True)

    def game_complete(self,
            final_state: pacai.core.gamestate.GameState,
            board_highlights: list[pacai.core.board.Highlight] | None = None,
            ) -> None:
        """ Update the UI with the game's final state. """

        self.update(final_state, board_highlights = board_highlights, force_draw_image = True)

        # Write the animation.
        if ((self._animation_path is not None) and (len(self._animation_frames) > 0)):
            ms_per_frame = int(1.0 / self._animation_fps * 1000.0)

            options = {
                'save_all': True,
                'append_images': self._animation_frames,
                'duration': ms_per_frame,
                'loop': 0,
                'optimize': False,
                'minimize_size': False,
            }

            if (self._animation_optimize):
                options['optimize'] = True
                options['minimize_size'] = True

            self._animation_frames[0].save(self._animation_path, None, **options)

    def wait_for_fps(self) -> None:
        """
        Wait/Sleep for long enough to get close to the desired FPS.
        Not all UIs will provide a real implementation for this method.
        """

        # No FPS limit is in place.
        if (self._fps <= 0):
            return

        # This is the first wait request, we don't have enough information yet.
        if (self._last_fps_wait is None):
            self._last_fps_wait = edq.util.time.Timestamp.now()
            return

        last_time = self._last_fps_wait
        now = edq.util.time.Timestamp.now()

        duration = now.sub(last_time)

        # Get the ideal number of milliseconds between frames.
        ideal_time_between_frames_ms = 1000.0 / self._fps

        # Get the wait time by comparing how long it has been since the last wait,
        # with the ideal wait between frames.
        wait_time_ms = ideal_time_between_frames_ms - duration.to_msecs()
        if (wait_time_ms > 0):
            self.sleep(int(wait_time_ms))

        # Mark the time this method completed.
        self._last_fps_wait = edq.util.time.Timestamp.now()

    def requires_sprites(self) -> bool:
        """ Check if this specific UI needs sprites or sprite sheets. """

        return True

    def sleep(self, sleep_time_ms: int) -> None:
        """
        Sleep for the specified number of ms.
        This is in a method so children can override with any more UI-specific sleep procedures.
        """

        time.sleep(sleep_time_ms / 1000.0)

    def close(self) -> None:
        """ Close the UI and release all owned resources. """

        if (self._user_input_device is not None):
            self._user_input_device.close()

    def get_user_inputs(self) -> list[pacai.core.action.Action]:
        """
        If a user input device is available,
        get the inputs via UserInputDevice.get_inputs().
        If no device is available, return an empty list.
        """

        if (self._user_input_device is None):
            return []

        return self._user_input_device.get_inputs()

    def draw_image(self, state: pacai.core.gamestate.GameState, **kwargs: typing.Any) -> PIL.Image.Image:
        """
        Visualize the state of the game as an image.
        This method is typically used for rendering the game to an animation.
        each call to this method is one frame in the animation.
        """

        if (self._sprite_sheet is None):
            raise ValueError("Cannot draw images without a sprite sheet.")

        # First, check the cache for the image.
        if (state.turn_count in self._image_cache):
            return self._image_cache[state.turn_count]

        image = self._get_static_image(state, **kwargs)

        canvas = PIL.ImageDraw.Draw(image)

        # Draw highlights.
        for (position, base_intensity) in self._highlights.items():
            start_coord = self._position_to_image_coords(position)
            end_coord = self._position_to_image_coords(position.add(pacai.core.board.Position(1, 1)))

            # Don't let the intensity go to zero.
            intensity = 0.10 + (0.9 * base_intensity)

            highlight_color = (
                int(self._sprite_sheet.highlight[0] * intensity),
                int(self._sprite_sheet.highlight[1] * intensity),
                int(self._sprite_sheet.highlight[2] * intensity),
            )

            canvas.rectangle([start_coord, end_coord], fill = tuple(highlight_color))

        # Draw non-agent (non-wall) markers.
        for (marker, positions) in state.board._nonwall_objects.items():
            if (marker.is_agent()):
                continue

            for position in positions:
                if (state.skip_draw(marker, position, static = False)):
                    continue

                sprite = self._get_sprite(state, position, marker = marker, animation_key = ANIMATION_KEY)
                self._place_sprite(position, sprite, image)

        # Draw non-static text.
        self._draw_position_text(state.get_nonstatic_text(), image)

        # Draw agent markers.
        for (marker, positions) in state.board._nonwall_objects.items():
            if (not marker.is_agent()):
                continue

            for position in positions:
                if (state.skip_draw(marker, position, static = False)):
                    continue

                last_action = state.get_last_agent_action(marker.get_agent_index())
                sprite = self._get_sprite(state, position, marker = marker, action = last_action, animation_key = ANIMATION_KEY)
                self._place_sprite(position, sprite, image)

        # Draw the footer (usually the score).
        footer_text = state.get_footer_text()
        if (footer_text is not None):
            (base_x, base_y) = self._position_to_image_coords(pacai.core.board.Position(state.board.height, 0))
            self._draw_text(footer_text, base_x, base_y, canvas)

        # Store this image in the cache.
        self._image_cache[state.turn_count] = image

        return image

    def _get_font(self, size: pacai.core.font.FontSize) -> PIL.ImageFont.FreeTypeFont:
        font = self._fonts.get(size, None)
        if (font is None):
            raise ValueError("Font has not been loaded.")

        return font

    def _get_static_image(self, state: pacai.core.gamestate.GameState, **kwargs: typing.Any) -> PIL.Image.Image:
        """
        Get the base image that only contains static objects.
        This method will handle caching the base static image.
        """

        if (self._sprite_sheet is None):
            raise ValueError("Cannot draw images without a sprite sheet.")

        # Check the cache.
        if (self._static_base_image is not None):
            return self._static_base_image.copy()

        # Height is +1 to leave room for the score.
        size = (
            state.board.width * self._sprite_sheet.width,
            (state.board.height + 1) * self._sprite_sheet.height,
        )

        # Add in an alpha channel to the background.
        background_color = list(self._sprite_sheet.background)
        background_color.append(255)

        image = PIL.Image.new('RGB', size, tuple(background_color))

        # Draw wall markers.
        for position in state.board.get_walls():
            if (state.skip_draw(pacai.core.board.MARKER_WALL, position, static = True)):
                continue

            adjacency = state.board.get_adjacent_walls(position)
            sprite = self._get_sprite(state, position, marker = pacai.core.board.MARKER_WALL, adjacency = adjacency, animation_key = ANIMATION_KEY)
            self._place_sprite(position, sprite, image)

        # Draw an additional static markers.
        for position in state.get_static_positions():
            for marker in state.board.get(position):
                if (state.skip_draw(marker, position, static = True)):
                    continue

                sprite = self._get_sprite(state, position, marker = marker, animation_key = ANIMATION_KEY)
                self._place_sprite(position, sprite, image)

        # Draw static text.
        self._draw_position_text(state.get_static_text(), image)

        # Cache the image.
        self._static_base_image = image.copy()

        return image

    def _draw_position_text(self, board_texts: list[pacai.core.font.BoardText], image: PIL.Image.Image) -> None:
        """ Draw text on a board position. """

        if (len(board_texts) == 0):
            return

        canvas = PIL.ImageDraw.Draw(image)
        for board_text in board_texts:
            # Base positions start in the upper left.
            (base_x, base_y) = self._position_to_image_coords(board_text.position)

            self._draw_text(board_text, base_x, base_y, canvas)

    def _draw_text(self,
            text: pacai.core.font.Text,
            base_x: int, base_y: int,
            canvas: PIL.ImageDraw.ImageDraw,
            ) -> None:
        """ Draw text to the board. """

        if (self._sprite_sheet is None):
            raise ValueError("Cannot draw text without a sprite sheet.")

        # Compute alignment offsets.
        vertical_offset = self._sprite_sheet.height * text.vertical_align.value
        horizontal_offset = self._sprite_sheet.width * text.horizontal_align.value

        y = base_y + vertical_offset
        x = base_x + horizontal_offset

        color = text.color
        if (color is None):
            color = self._sprite_sheet.text

        canvas.text((x, y), text.text, color,
                self._get_font(text.size),
                anchor = text.anchor,
                align = 'center')

    def _get_sprite(self, state: pacai.core.gamestate.GameState, position: pacai.core.board.Position, **kwargs: typing.Any) -> PIL.Image.Image:
        """ Get the requested sprite. """

        if (self._sprite_sheet is None):
            raise ValueError("Sprites are not loaded in this UI.")

        return state.sprite_lookup(self._sprite_sheet, position, **kwargs)

    def _place_sprite(self, position: pacai.core.board.Position, sprite: PIL.Image.Image, image: PIL.Image.Image) -> None:
        image_coordinates = self._position_to_image_coords(position)

        # Overlay the sprite onto the image.
        # Note that the same image is used as the mask, since sprites will usually have alpha channels
        # (so the transparent parts will not get drawn).
        image.paste(sprite, image_coordinates, sprite)

    def _position_to_image_coords(self, position: pacai.core.board.Position) -> tuple[int, int]:
        """
        Get the image coordinates (in pixels) for this position.
        Returns: (x, y).
        """

        if (self._sprite_sheet is None):
            raise ValueError("Sprites are not loaded.")

        return self._sprite_sheet.position_to_pixels(position)

    @abc.abstractmethod
    def draw(self, state: pacai.core.gamestate.GameState, **kwargs: typing.Any) -> None:
        """
        Visualize the state of the game to the UI.
        This is the typically the main override point for children.
        Note that how this method visualizes the game completely unrelated
        to how the draw_image() method works.
        draw() will render to whatever the specific UI for the child class is,
        while draw_image() specifically creates an image which will be used for animations.
        If the child UI is also image-based than it can leverage draw_image(),
        but there is no requirement to do that.
        """

def set_cli_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """
    Set common CLI arguments.
    This is a sibling to init_from_args(), as the arguments set here can be interpreted there.
    """

    parser.add_argument('--ui', dest = 'ui',
            action = 'store', type = str, default = pacai.util.alias.UI_WEB.short,
            help = ('Set the UI/graphics to use (default: %(default)s).'
                    + ' Builtin options:'
                    + f' `{pacai.util.alias.UI_NULL.short}` (`{pacai.util.alias.UI_NULL.long}`)'
                    +       ' -- Do not show any ui/graphics (best if you want to run fast and just need the result),'
                    + f' `{pacai.util.alias.UI_STDIO.short}` (`{pacai.util.alias.UI_STDIO.long}`)'
                    +       ' -- Use stdin/stdout from the terminal,'
                    + f' `{pacai.util.alias.UI_TK.short}` (`{pacai.util.alias.UI_TK.long}`)'
                    +       ' -- Use Tk/tkinter (must already be installed) to open a window,'
                    + f' `{pacai.util.alias.UI_WEB.short}` (`{pacai.util.alias.UI_WEB.long}`)'
                    +       ' -- Launch a browser window (default).'))

    parser.add_argument('--show-training-ui', dest = 'show_training_ui',
            action = 'store_true', default = False,
            help = 'Show the specified UI (--ui) for training epochs/games. Otherwise, a null UI will be used (default: %(default)s).')

    parser.add_argument('--fps', dest = 'fps',
            action = 'store', type = int, default = DEFAULT_FPS,
            help = ('Set the visual speed (frames per second) for UIs (default: %(default)s).'
                    + ' Lower values are slower, and higher values are faster.'))

    parser.add_argument('--animation-path', dest = 'animation_path',
            action = 'store', type = str, default = None,
            help = ('If specified, store an animated recording of the game at the specified location.'
                    + f" This path must have one of the following extensions: {ANIMATION_EXTS}."))

    parser.add_argument('--animation-fps', dest = 'animation_fps',
            action = 'store', type = int, default = DEFAULT_ANIMATION_FPS,
            help = 'Set the fps of the animation (default: %(default)s).')

    parser.add_argument('--animation-skip-frames', dest = 'animation_skip_frames',
            action = 'store', type = int, default = DEFAULT_ANIMATION_SKIP_FRAMES,
            help = ('Only include every X frames in the animation.'
                    + ' The default (1) means that every frame will be included.'
                    + ' Using higher values can reduce the animations size and processing time'
                    + ' (since there are fewer frames).'))

    parser.add_argument('--animation-optimize', dest = 'animation_optimize',
            action = 'store_true', default = DEFAULT_ANIMATION_OPTIMIZE,
            help = 'Optimize the animation to reduce file size (will take longer) (default: %(default)s).')

    return parser

def init_from_args(
        args: argparse.Namespace,
        num_uis: int = 0,
        null_out_uis: int = 0,
        additional_args: dict | None = None,
        ) -> argparse.Namespace:
    """
    Take in args from a parser that was passed to set_cli_args(),
    and initialize the proper components.
    Constructed UIs will be placed `args._uis`.
    If `num_uis` is not provided (or <= 0),
    then `args.num_games` + `args.num_training` will be used.
    If `null_out_uis` is > 0, then at most that number of UIs (starting at the beginning)
    will be converted to null UIs.
    This will not change the total number of UIs, just null out the first number of UIs.
    """

    ui_args = {
        'fps': args.fps,
        'animation_path': args.animation_path,
        'animation_fps': args.animation_fps,
        'animation_skip_frames': args.animation_skip_frames,
        'animation_optimize': args.animation_optimize,
    }

    if (additional_args is not None):
        ui_args.update(additional_args)

    if (num_uis <= 0):
        num_uis = args.num_games + args.num_training

    uis = []
    for i in range(num_uis):
        ui_name = args.ui
        if (i < null_out_uis):
            ui_name = pacai.util.alias.UI_NULL.long

        uis.append(pacai.util.reflection.new_object(ui_name, **ui_args))

    setattr(args, '_uis', uis)

    return args
