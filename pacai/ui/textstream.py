import atexit
import platform
import queue
import sys
import termios
import threading
import typing

import pacai.core.action
import pacai.core.ui

WASD_CHAR_MAPPING: dict[str, pacai.core.action.Action] = {
    'w': pacai.core.action.NORTH,
    'a': pacai.core.action.WEST,
    's': pacai.core.action.SOUTH,
    'd': pacai.core.action.EAST,
    'W': pacai.core.action.NORTH,
    'A': pacai.core.action.WEST,
    'S': pacai.core.action.SOUTH,
    'D': pacai.core.action.EAST,
    ' ': pacai.core.action.STOP,
}
""" A character to action mapping using the common WASD scheme. """

class TextStreamUserInputDevice(pacai.core.ui.UserInputDevice):
    """
    A user input device that watches a text stream for input.
    The text stream could be a wide range of things,
    including a file or stdin.
    The target text stream will be closed when this device is closed.
    """

    def __init__(self, input_stream: typing.TextIO, char_mapping: dict[str, pacai.core.action.Action]) -> None:
        self._input_stream: typing.TextIO = input_stream
        """ Where to get input from. """

        self._char_mapping: dict[str, pacai.core.action.Action] = char_mapping
        """ Map characters to actions. """

        self._chars_queue: queue.Queue = queue.Queue()
        """ Used to store characters coming from stdin. """

        self._thread: threading.Thread = threading.Thread(target = _watch_stdin, args = (self._input_stream, self._chars_queue))
        """ The thread that does the actual reading. """

        self._thread.start()

    def get_inputs(self) -> list[pacai.core.action.Action]:
        output: list[pacai.core.action.Action] = []
        while (not self._chars_queue.empty()):
            char = self._chars_queue.get(block = False)
            if (char in self._char_mapping):
                output.append(self._char_mapping[char])

        return output

    def close(self) -> None:
        self._input_stream.close()
        self._thread.join()

    def __dict__(self):
        raise ValueError(f"This class ('{type(self).__qualname__}') cannot be serialized.")

class StdinUserInputDevice(TextStreamUserInputDevice):
    """
    A user input device that gets input from stdin.
    Using stdin is special because it may be coming from a terminal.
    """

    def __init__(self, char_mapping: dict[str, pacai.core.action.Action]) -> None:
        self._old_settings: list | None = None
        """ Keep track of the old terminal settings so we can reset properly. """

        self._set_stdin_attributes()

        super().__init__(sys.stdin, char_mapping)

    def _set_stdin_attributes(self):
        # If we are not a tty, then there is nothing special to do.
        if (not sys.stdin.isatty()):
            return

        # Do a platform check for POSIX.
        if (platform.system() == "Windows"):
            raise ValueError("Stdin user input devices are not supported on Windows.")

        self._old_settings = termios.tcgetattr(sys.stdin)
        """ Keep track of the old setting so we can reset properly. """

        # Since the behavior of the terminal can be changed by this class,
        # ensure everything is reset when the program exits.
        atexit.register(self._reset_stdin)

        new_settings = termios.tcgetattr(sys.stdin)

        # Modify lflags.
        # Remove echo and canonical (line-by-line) mode.
        new_settings[3] = new_settings[3] & ~(termios.ECHO | termios.ICANON)

        # Modify CC flags.
        # Set non-canonical mode min chars and timeout.
        new_settings[6][termios.VMIN] = 1
        new_settings[6][termios.VTIME] = 0

        termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, new_settings)

    def close(self) -> None:
        self._reset_stdin()
        super().close()

    def _reset_stdin(self):
        if (self._old_settings is not None):
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old_settings)
            self._old_settings = None

def _watch_stdin(input_stream: typing.TextIO, result_queue: queue.Queue) -> None:
    """
    A thread worker to watch stdin and relay the input.
    """

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
