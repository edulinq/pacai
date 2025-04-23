import sys
import time
import tkinter

import PIL.Image
import PIL.ImageTk

import pacai.core.action
import pacai.core.gamestate
import pacai.core.ui

TK_BASE_NAME: str = 'pacai'
DEATH_SLEEP_TIME_SECS: float = 0.5

MIN_WINDOW_HEIGHT: int = 100
MIN_WINDOW_WIDTH: int = 100

WASD_CHAR_MAPPING: dict[str, pacai.core.action.Action] = {
    'w': pacai.core.action.NORTH,
    'a': pacai.core.action.WEST,
    's': pacai.core.action.SOUTH,
    'd': pacai.core.action.EAST,
    'W': pacai.core.action.NORTH,
    'A': pacai.core.action.WEST,
    'S': pacai.core.action.SOUTH,
    'D': pacai.core.action.EAST,
    'space': pacai.core.action.STOP,
}
""" A character to action mapping using the common WASD scheme. """

ARROW_CHAR_MAPPING: dict[str, pacai.core.action.Action] = {
    'Up': pacai.core.action.NORTH,
    'Left': pacai.core.action.WEST,
    'Down': pacai.core.action.SOUTH,
    'Right': pacai.core.action.EAST,
    'space': pacai.core.action.STOP,
}
""" A character to action mapping using the arrow keys. """

class TKUserInputDevice(pacai.core.ui.UserInputDevice):
    """
    Use TK to capture keyboard inputs on the window.
    """

    def __init__(self,
            char_mapping: dict[str, pacai.core.action.Action] = WASD_CHAR_MAPPING,
            **kwargs) -> None:
        self._char_mapping: dict[str, pacai.core.action.Action] = char_mapping
        """ Map characters to actions. """

        self._actions: list[pacai.core.action.Action] = []
        """ The currently seen actions. """

    def get_inputs(self) -> list[pacai.core.action.Action]:
        actions = self._actions
        self._actions = []

        return actions

    def register_root(self, tk_root: tkinter.Tk) -> None:
        tk_root.bind("<KeyPress>", self._key_press)
        tk_root.bind("<KeyRelease>", self._key_release)
        tk_root.bind("<FocusIn>", self._clear)
        tk_root.bind("<FocusOut>", self._clear)

    def _clear(self, event) -> None:
        self._actions = []

    def _key_press(self, event) -> None:
        if (event.keysym in self._char_mapping):
            self._actions.append(self._char_mapping[event.keysym])

    def _key_release(self, event) -> None:
        pass

class TKUI(pacai.core.ui.UI):
    """
    A UI that uses TK/TKinter to open a window and draw the game in the window.
    Although the `tkinter` package is part of the Python standard library,
    TK must already be installed on your system.
    See:
     - https://docs.python.org/3/library/tkinter.html
     - https://tkdocs.com/tutorial/install.html
    """

    def __init__(self, title: str = 'pacai', **kwargs) -> None:
        input_device = TKUserInputDevice(**kwargs)
        super().__init__(user_input_device = input_device, **kwargs)

        if (title != 'pacai'):
            title = 'pacai - %s' % (title)

        self._title: str = title
        """ The title of the TK window. """

        self._root: tkinter.Tk = tkinter.Tk(baseName = TK_BASE_NAME)
        """ The root/base TK element. """

        self._canvas: tkinter.Canvas | None = None
        """ The TK drawing/rendering area. """

        self._image_area: int = -1
        """ The TK area where images will be rendered. """

        self._height: int = 0
        """ Height of the TK window. """

        self._width: int = 0
        """ Width of the TK window. """

        self._window_closed: bool = False
        """ Indicate that the TK window has been closed. """

    def game_start(self, initial_state: pacai.core.gamestate.GameState) -> None:
        self._init_tk(initial_state)
        super().game_start(initial_state)

    def game_complete(self, final_state: pacai.core.gamestate.GameState) -> None:
        super().game_complete(final_state)

        if (self._canvas is not None):
            self._canvas.delete("all")

    def _init_tk(self, state: pacai.core.gamestate.GameState) -> None:
        """
        Initialize all the TK components using the initial game state.
        """

        self._root.protocol('WM_DELETE_WINDOW', self._handle_window_closed)
        self._root.minsize(width = MIN_WINDOW_WIDTH, height = MIN_WINDOW_HEIGHT)
        self._root.resizable(True, True)
        self._root.title(self._title)
        self._root.bind("<Configure>", self._handle_resize)

        # Height is +1 for the score.
        self._height = max(MIN_WINDOW_HEIGHT, (state.board.height + 1) * self._sprite_sheet.height)
        self._width = max(MIN_WINDOW_WIDTH, state.board.width * self._sprite_sheet.width)

        self._canvas = tkinter.Canvas(self._root, height = self._height, width = self._width, highlightthickness = 0)

        self._image_area = self._canvas.create_image(0, 0, image = None, anchor = tkinter.NW)
        self._canvas.pack(fill = 'both', expand = True)

        # Initialize the user input (keyboard).
        if (isinstance(self.user_input_device, TKUserInputDevice)):
            self.user_input_device.register_root(self._root)

    def draw(self, state: pacai.core.gamestate.GameState) -> None:
        if (self._window_closed):
            self._cleanup()
            return

        # Ensure no pre-mature draws.
        if (self._canvas is None):
            raise ValueError("Cannot draw before game has started.")

        # Leverage the existing draw_image() method to produce an image.
        image = self.draw_image(state)

        # Check if we need to resize the image.
        if ((self._height != image.height) or (self._width != image.width)):
            image = image.resize((self._width, self._height), resample = PIL.Image.Resampling.LANCZOS)

        # Convert the image into a tk image.
        tk_image = PIL.ImageTk.PhotoImage(image)
        self._canvas.itemconfig(self._image_area, image = tk_image)

        self._root.update_idletasks()
        self._root.update()

    def sleep(self, sleep_time_ms: int) -> None:
        self._root.after(sleep_time_ms, None)  # type: ignore

    def _handle_resize(self, event):
        """ Handle TK configure (resize) events. """

        if (self._width == event.width and self._height == event.height):
            return

        # Ignore resize requests that are for a single pixel.
        # (These requests are sometimes generated from OSX.)
        if (event.width == 1 and event.height == 1):
            return

        if (self._canvas is None):
            return

        self._width = max(MIN_WINDOW_WIDTH, event.width)
        self._height = max(MIN_WINDOW_HEIGHT, event.height)

        self._canvas.config(width = self._width, height = self._height)
        self._canvas.pack(fill = 'both', expand = True)

    def _handle_window_closed(self, event = None):
        """ Handle TK window close events. """

        self._window_closed = True

    def _cleanup(self, exit = True):
        """
        The TK window has been killed, clean up.
        This is one of the rare case where a non-bin will call sys.exit().
        """

        # Sleep for a short period, so the last state of the game can be seen.
        time.sleep(DEATH_SLEEP_TIME_SECS)

        if (self._root is not None):
            self._root.destroy()
            self._root = None

        if (exit):
            sys.exit(0)
