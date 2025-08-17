import sys
import time
import tkinter
import typing

import PIL.Image
import PIL.ImageTk

import pacai.core.action
import pacai.core.board
import pacai.core.gamestate
import pacai.core.ui

TK_BASE_NAME: str = 'pacai'
DEATH_SLEEP_TIME_SECS: float = 0.5

MIN_WINDOW_HEIGHT: int = 100
MIN_WINDOW_WIDTH: int = 100

_tk_root: tkinter.Tk | None = None

_tk_window_count: int = 0

class TkUserInputDevice(pacai.core.ui.UserInputDevice):
    """
    Use Tk to capture keyboard inputs on the window.
    """

    def __init__(self,
            char_mapping: dict[str, pacai.core.action.Action] | None = None,
            **kwargs: typing.Any) -> None:
        if (char_mapping is None):
            char_mapping = pacai.core.ui.DUAL_CHAR_MAPPING

        self._char_mapping: dict[str, pacai.core.action.Action] = char_mapping
        """ Map characters to actions. """

        self._actions: list[pacai.core.action.Action] = []
        """ The currently seen actions. """

    def get_inputs(self) -> list[pacai.core.action.Action]:
        actions = self._actions
        self._actions = []

        return actions

    def register_root(self, tk_window: tkinter.Tk | tkinter.Toplevel) -> None:
        """ Register/Bind this handler to a root Tk element. """

        tk_window.bind("<KeyPress>", self._key_press)
        tk_window.bind("<KeyRelease>", self._key_release)
        tk_window.bind("<FocusIn>", self._clear)
        tk_window.bind("<FocusOut>", self._clear)

    def _clear(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """ Handle a call to clear the current keys. """

        self._actions = []

    def _key_press(self, event: typing.Any) -> None:
        """ Handle a key being pressed. """

        if (event.keysym in self._char_mapping):
            self._actions.append(self._char_mapping[event.keysym])

    def _key_release(self, event: typing.Any) -> None:
        """ Handle a key being released. """

class TkUI(pacai.core.ui.UI):
    """
    A UI that uses Tk/tkinter to open a window and draw the game in the window.
    Although the `tkinter` package is part of the Python standard library,
    Tk must already be installed on your system.
    See:
     - https://docs.python.org/3/library/tkinter.html
     - https://tkdocs.com/tutorial/install.html
    """

    def __init__(self, title: str = 'pacai', **kwargs: typing.Any) -> None:
        input_device = TkUserInputDevice(**kwargs)
        super().__init__(user_input_device = input_device, **kwargs)

        if (title != 'pacai'):
            title = f"pacai - {title}"

        self._title: str = title
        """ The title of the Tk window. """

        self._window: tkinter.Tk | tkinter.Toplevel | None = None
        """ The root/base Tk element. """

        self._canvas: tkinter.Canvas | None = None
        """ The Tk drawing/rendering area. """

        self._image_area: int = -1
        """ The Tk area where images will be rendered. """

        self._height: int = 0
        """ Height of the Tk window. """

        self._width: int = 0
        """ Width of the Tk window. """

        self._window_closed: bool = False
        """ Indicate that the Tk window has been closed. """

    def game_start(self,
            initial_state: pacai.core.gamestate.GameState,
            board_highlights: list[pacai.core.board.Highlight] | None = None,
            ) -> None:
        self._init_tk(initial_state)
        super().game_start(initial_state, board_highlights = board_highlights)

    def game_complete(self,
            final_state: pacai.core.gamestate.GameState,
            board_highlights: list[pacai.core.board.Highlight] | None = None,
            ) -> None:
        super().game_complete(final_state, board_highlights = board_highlights)

        if (self._canvas is not None):
            self._canvas.delete("all")

    def _init_tk(self, state: pacai.core.gamestate.GameState) -> None:
        """
        Initialize all the Tk components using the initial game state.
        """

        if (self._sprite_sheet is None):
            raise ValueError("Sprites are not loaded in this UI.")

        self._window = _get_tk_window()

        self._window.protocol('WM_DELETE_WINDOW', self._handle_window_closed)
        self._window.minsize(width = MIN_WINDOW_WIDTH, height = MIN_WINDOW_HEIGHT)
        self._window.resizable(True, True)
        self._window.title(self._title)
        self._window.bind("<Configure>", self._handle_resize)

        # Don't start the window too large.
        max_initial_height = self._window.winfo_screenheight() - 100
        max_initial_width = self._window.winfo_screenwidth() - 100

        # Height is +1 for the score.
        self._height = min(max_initial_height, max(MIN_WINDOW_HEIGHT, (state.board.height + 1) * self._sprite_sheet.height))
        self._width = min(max_initial_width, max(MIN_WINDOW_WIDTH, state.board.width * self._sprite_sheet.width))

        self._canvas = tkinter.Canvas(self._window, height = self._height, width = self._width, highlightthickness = 0)

        self._image_area = self._canvas.create_image(0, 0, image = None, anchor = tkinter.NW)
        self._canvas.pack(fill = 'both', expand = True)

        # Initialize the user input (keyboard).
        if (isinstance(self._user_input_device, TkUserInputDevice)):
            self._user_input_device.register_root(self._window)

    def draw(self, state: pacai.core.gamestate.GameState, **kwargs: typing.Any) -> None:
        if (self._window_closed):
            self._cleanup(call_exit = True)
            return

        # Ensure no pre-mature draws.
        if ((self._window is None) or (self._canvas is None)):
            raise ValueError("Cannot draw before game has started.")

        # Leverage the existing draw_image() method to produce an image.
        image = self.draw_image(state)

        # Check if we need to resize the image.
        if ((self._height != image.height) or (self._width != image.width)):
            image = image.resize((self._width, self._height), resample = PIL.Image.Resampling.LANCZOS)

        # Convert the image into a tk image.
        tk_image = PIL.ImageTk.PhotoImage(image)
        self._canvas.itemconfig(self._image_area, image = tk_image)

        self._window.update_idletasks()
        self._window.update()

    def sleep(self, sleep_time_ms: int) -> None:
        if (self._window is not None):
            self._window.after(sleep_time_ms, None)  # type: ignore

    def close(self) -> None:
        self._cleanup(call_exit = False)

    def _handle_resize(self, event: tkinter.Event) -> None:
        """ Handle Tk configure (resize) events. """

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

    def _handle_window_closed(self, **kwargs: typing.Any) -> None:
        """ Handle Tk window close events. """

        self._window_closed = True

    def _cleanup(self, call_exit: bool = True) -> None:
        """
        The Tk window has been killed, clean up.
        This is one of the rare case where a non-bin will call sys.exit().
        """

        # Sleep for a short period, so the last state of the game can be seen.
        if (not call_exit):
            time.sleep(DEATH_SLEEP_TIME_SECS)

        if (self._window is not None):
            _cleanup_tk_window(self._window)

        if (call_exit):
            sys.exit(0)

def _get_tk_window() -> tkinter.Tk | tkinter.Toplevel:
    global _tk_root  # pylint: disable=global-statement
    global _tk_window_count  # pylint: disable=global-statement

    _tk_window_count += 1

    if (_tk_root is None):
        _tk_root = tkinter.Tk(baseName = TK_BASE_NAME)
        return _tk_root

    return tkinter.Toplevel()

def _cleanup_tk_window(window: tkinter.Tk | tkinter.Toplevel) -> None:
    global _tk_root  # pylint: disable=global-statement
    global _tk_window_count  # pylint: disable=global-statement

    window.destroy()

    _tk_window_count -= 1
    if (_tk_window_count == 0):
        _tk_root = None
