import abc
import os
import time

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

import pacai.core.action
import pacai.core.gamestate
import pacai.core.spritesheet
import pacai.util.time

DEFAULT_ANIMATION_FPS: int = 10
MIN_ANIMATION_FPS: int = 1
FONT_SIZE_OFFSET: int = -14

THIS_DIR: str = os.path.join(os.path.dirname(os.path.realpath(__file__)))
DEFAULT_FONT_PATH: str = os.path.join(THIS_DIR, '..', 'resources', 'fonts', 'roboto', 'RobotoMono-Regular.ttf')
DEFAULT_SPRITE_SHEET_PATH: str = os.path.join(THIS_DIR, '..', 'resources', 'spritesheets', 'generic.json')

ANIMATION_KEY: str = 'UI.draw_image'

ANIMATION_EXTS: set[str] = {'.gif', '.webp'}
""" The allowed extensions for animation files. """

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

        pass

    def close(self) -> None:
        """ Close the user input channel and release all owned resources. """

        pass

class UI(abc.ABC):
    """
    UIs represent the basic way that a game interacts with the user,
    by displaying the state of the game and taking input from the user (if applicable).
    """

    def __init__(self,
            user_input_device: UserInputDevice | None = None,
            fps: int = -1,
            animation_path: str | None = None, animation_optimize: bool = False,
            animation_fps: int = DEFAULT_ANIMATION_FPS, animation_skip_frames: int = 1,
            sprite_sheet_path: str = DEFAULT_SPRITE_SHEET_PATH,
            font_path: str = DEFAULT_FONT_PATH,
            **kwargs) -> None:
        self.user_input_device: UserInputDevice | None = user_input_device
        """ The device to use to get user input. """

        self._fps: int = fps
        """
        The desired frames per second this game will be displayed at.
        Zero or lower values will be ignored.
        This is just a suggestion that the game will try an accommodate.
        Not all UIs will observe fps.
        """

        self._last_fps_wait: pacai.util.time.Timestamp | None = None
        """
        Keep track of the last time the UI waited to adjust the fps.
        We need this information to compute the next wait time.
        """

        self._update_count: int = 0
        """ Keep track of the number of times update() has been called. """

        self._animation_path: str | None = animation_path
        """ If specified, create a animation and write it to this location after the game completes. """

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

        self._walls_image: PIL.Image.Image | None = None
        """
        Cache an image that just has the walls drawn.
        This can be reused as the base image every time we draw an image (since the walls do not change).
        """

        self._sprite_sheet: pacai.core.spritesheet.SpriteSheet = pacai.core.spritesheet.load(sprite_sheet_path)
        """ The sprite sheet to use for this UI. """

        self._font: PIL.ImageFont.FreeTypeFont = PIL.ImageFont.truetype(font_path, self._sprite_sheet.height + FONT_SIZE_OFFSET)
        """ The font to use for this UI. """

        if (self._animation_path is not None):
            if (os.path.splitext(self._animation_path)[-1] not in ANIMATION_EXTS):
                raise ValueError("Animation path must have one of the following extensions %s, found '%s'." % (ANIMATION_EXTS, self._animation_path))

    def update(self, state: pacai.core.gamestate.GameState, force_draw_image: bool = False) -> None:
        """
        Update the UI with the current state of the game.
        This is the main entry point for the game into the UI.
        """

        self.wait_for_fps()

        if ((self._animation_path is not None) and (force_draw_image or (self._update_count % self._animation_skip_frames == 0))):
            image = self.draw_image(state)
            self._animation_frames.append(image)

        self.draw(state)

        self._update_count += 1

    def game_start(self, initial_state: pacai.core.gamestate.GameState) -> None:
        """ Initialize the UI with the game's initial state. """

        self.update(initial_state, force_draw_image = True)

    def game_complete(self, final_state: pacai.core.gamestate.GameState) -> None:
        """ Update the UI with the game's final state. """

        self.update(final_state, force_draw_image = True)

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
            self._last_fps_wait = pacai.util.time.now()
            return

        last_time = self._last_fps_wait
        now = pacai.util.time.now()

        duration = now.sub(last_time)

        # Get the ideal number of milliseconds between frames.
        ideal_time_between_frames_ms = 1000.0 / self._fps

        # Get the wait time by comparing how long it has been since the last wait,
        # with the ideal wait between frames.
        wait_time_ms = ideal_time_between_frames_ms - duration.to_msecs()
        if (wait_time_ms > 0):
            time.sleep(wait_time_ms / 1000.0)

        # Mark the time this method completed.
        self._last_fps_wait = pacai.util.time.now()

    def close(self) -> None:
        """ Close the UI and release all owned resources. """

        if (self.user_input_device is not None):
            self.user_input_device.close()

    def get_user_inputs(self) -> list[pacai.core.action.Action]:
        """
        If a user input device is available,
        get the inputs via UserInputDevice.get_inputs().
        If no device is available, return an empty list.
        """

        if (self.user_input_device is None):
            return []

        return self.user_input_device.get_inputs()

    def draw_image(self, state: pacai.core.gamestate.GameState) -> PIL.Image.Image:
        """
        Visualize the state of the game as an image.
        This method is typically used for rendering the game to an animation.
        each call to this method is one frame in the animation.
        """

        if (self._walls_image is None):
            # Height is +1 to leave room for the score.
            size = (
                state.board.width * self._sprite_sheet.width,
                (state.board.height + 1) * self._sprite_sheet.height,
            )

            # Add in the alpha channel to the background.
            background_color = list(self._sprite_sheet.background)
            background_color.append(255)

            image = PIL.Image.new('RGB', size, tuple(background_color))
        else:
            image = self._walls_image.copy()

        # Draw wall markers.
        for position in state.board.get_walls():
            adjacency = state.board.get_adjacent_walls(position)
            sprite = self._sprite_sheet.get_sprite(pacai.core.board.MARKER_WALL, adjacency = adjacency, animation_key = ANIMATION_KEY)
            self._place_sprite(position, sprite, image)

        if (self._walls_image is None):
            self._walls_image = image.copy()

        # Draw non-agent (non-wall) markers.
        for (marker, positions) in state.board._all_objects.items():
            if (marker.is_wall() or marker.is_agent()):
                continue

            for position in positions:
                sprite = self._sprite_sheet.get_sprite(marker, animation_key = ANIMATION_KEY)
                self._place_sprite(position, sprite, image)

        # Draw agent markers.
        for (marker, positions) in state.board._all_objects.items():
            if (not marker.is_agent()):
                continue

            for position in positions:
                last_action = state.last_agent_actions.get(marker.get_agent_index(), None)
                sprite = self._sprite_sheet.get_sprite(marker, action = last_action, animation_key = ANIMATION_KEY)
                self._place_sprite(position, sprite, image)

        # Draw the score.
        score_image_coordinates = (0, state.board.height * self._sprite_sheet.height)
        score_text = "Score: %d" % (state.score)
        canvas = PIL.ImageDraw.Draw(image)
        canvas.text(score_image_coordinates, score_text, self._sprite_sheet.text, self._font)

        return image

    def _place_sprite(self, position: pacai.core.board.Position, sprite: PIL.Image.Image, image: PIL.Image.Image):
        image_coordinates = (position.col * self._sprite_sheet.width, position.row * self._sprite_sheet.height)

        # Overlay the sprite onto the image.
        # Note that the same image is used as the mask, since sprites will usually have alpha channels
        # (so the transparent parts will not get drawn).
        image.paste(sprite, image_coordinates, sprite)

    @abc.abstractmethod
    def draw(self, state: pacai.core.gamestate.GameState) -> None:
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

        pass
