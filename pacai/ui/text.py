import atexit
import queue
import sys
import termios  # pylint: disable=import-error
import threading
import typing

import pacai.core.action
import pacai.core.board
import pacai.core.gamestate
import pacai.core.ui

class TextStreamUserInputDevice(pacai.core.ui.UserInputDevice):
    """
    A user input device that watches a text stream for input.
    The text stream could be a wide range of things,
    including a file or stdin.
    The target text stream will be closed when this device is closed.
    If the target stream is a tty (e.g., stdin),
    then the tty's attributes will be adjusted for streaming input.
    """

    def __init__(self,
            input_stream: typing.TextIO,
            char_mapping: dict[str, pacai.core.action.Action] | None = None,
            **kwargs: typing.Any) -> None:
        self._input_stream: typing.TextIO = input_stream
        """ Where to get input from. """

        if (char_mapping is None):
            char_mapping = pacai.core.ui.DUAL_CHAR_MAPPING

        self._char_mapping: dict[str, pacai.core.action.Action] = char_mapping
        """ Map characters to actions. """

        self._chars_queue: queue.Queue = queue.Queue()
        """ Used to store characters coming from the input stream. """

        self._thread: threading.Thread = threading.Thread(target = _watch_text_stream, args = (self._input_stream, self._chars_queue))
        """ The thread that does the actual reading. """

        self._old_settings: list | None = None
        """ Keep track of the old tty settings so we can reset properly. """

        self._set_tty_attributes()

        self._thread.start()

    def get_inputs(self) -> list[pacai.core.action.Action]:
        output: list[pacai.core.action.Action] = []
        while (not self._chars_queue.empty()):
            char = self._chars_queue.get(block = False)
            if (char in self._char_mapping):
                output.append(self._char_mapping[char])

        return output

    def close(self) -> None:
        self._reset_tty_attributes()
        self._input_stream.close()
        self._thread.join()

        super().close()

    def __dict__(self) -> dict[str, typing.Any]:  # type: ignore[override]
        """ Do not allow for serialization because of the threads and streams. """

        raise ValueError(f"This class ('{type(self).__qualname__}') cannot be serialized.")

    def _set_tty_attributes(self) -> None:
        """ If the target stream is a tty, then set properties for better streaming input. """

        # If we are not a tty, then there is nothing special to do.
        if (not self._input_stream.isatty()):
            return

        # Do a platform check for POSIX.
        if (sys.platform.startswith("win")):
            raise ValueError("Terminal (tty) user input devices are not supported on Windows.")

        self._old_settings = termios.tcgetattr(self._input_stream)

        # Since the behavior of the terminal can be changed by this class,
        # ensure everything is reset when the program exits.
        atexit.register(self._reset_tty_attributes)

        new_settings = termios.tcgetattr(self._input_stream)

        # Modify lflags.
        # Remove echo and canonical (line-by-line) mode.
        new_settings[3] = new_settings[3] & ~(termios.ECHO | termios.ICANON)

        # Modify CC flags.
        # Set non-canonical mode min chars and timeout.
        new_settings[6][termios.VMIN] = 1
        new_settings[6][termios.VTIME] = 0

        termios.tcsetattr(self._input_stream, termios.TCSAFLUSH, new_settings)

    def _reset_tty_attributes(self) -> None:
        if (self._old_settings is not None):
            # Note that Windows does not have these settings.
            if (hasattr(termios, 'tcsetattr') and hasattr(termios, 'TCSADRAIN')):
                termios.tcsetattr(self._input_stream, termios.TCSADRAIN, self._old_settings)  # type: ignore[attr-defined,unused-ignore]

            self._old_settings = None

def _watch_text_stream(input_stream: typing.TextIO, result_queue: queue.Queue) -> None:
    """ A thread worker to watch a text stream and relay the input. """

    while (True):
        try:
            next_char = input_stream.read(1)
        except ValueError:
            # Should indicate that the stream was closed.
            return

        # Check for an EOF.
        if ((next_char is None) or (len(next_char) == 0)):
            return

        result_queue.put(next_char, block = False)

class TextUI(pacai.core.ui.UI):
    """
    A simple UI that renders the game to a text stream and takes input from another text stream.
    This UI will be simple and generally meant for debugging.
    """

    def __init__(self,
            input_stream: typing.TextIO,
            output_stream: typing.TextIO,
            **kwargs: typing.Any) -> None:
        input_device = TextStreamUserInputDevice(input_stream, **kwargs)
        super().__init__(user_input_device = input_device, **kwargs)

        self._output_stream: typing.TextIO = output_stream
        """ The stream output will be sent to. """

    def draw(self, state: pacai.core.gamestate.GameState, **kwargs: typing.Any) -> None:
        grid = state.board.to_grid()
        for row in grid:
            line = ''.join([self._translate_marker(marker, state) for marker in row])
            self._output_stream.write(line + "\n")

        self._output_stream.write(f"Score: {state.score}\n")

        if (state.game_over):
            self._output_stream.write('Game Over!\n')

        self._output_stream.write("\n")
        self._output_stream.flush()

    def _translate_marker(self, marker: pacai.core.board.Marker, state: pacai.core.gamestate.GameState) -> str:
        """
        Convert a marker to a string.
        This is generally trivial (since a marker is already a string),
        but this allows children to implement special conversions.
        """

        return marker

class StdioUI(TextUI):
    """
    A convenience class for a TextUI using stdin and stdout.
    """

    def __init__(self, **kwargs: typing.Any) -> None:
        super().__init__(sys.stdin, sys.stdout, **kwargs)
