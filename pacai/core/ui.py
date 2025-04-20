import abc
import time

import pacai.core.action
import pacai.core.gamestate
import pacai.util.time

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

    def update(self, state: pacai.core.gamestate.GameState) -> None:
        """
        Update the UI with the current state of the game.
        This is the main entry point for the game into the UI.
        """

        self.wait_for_fps()
        self.draw(state)

    def game_start(self, initial_state: pacai.core.gamestate.GameState) -> None:
        """ Initialize the UI with the game's initial state. """

        self.update(initial_state)

    def game_complete(self, final_state: pacai.core.gamestate.GameState) -> None:
        """ Update the UI with the game's final state. """

        self.update(final_state)

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

    @abc.abstractmethod
    def draw(self, state: pacai.core.gamestate.GameState) -> None:
        """ Visualize the state of the game to the UI. """

        pass
