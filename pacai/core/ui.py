import abc

import pacai.core.action
import pacai.core.gamestate

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

class UI(abc.ABC):
    """
    UIs represent the basic way that a game interacts with the user,
    by displaying the state of the game and taking input from the user (if applicable).
    """

    @abc.abstractmethod
    def game_start(self, initial_state: pacai.core.gamestate.GameState) -> None:
        """ Initialize the UI with the game's initial state. """

        pass

    @abc.abstractmethod
    def update(self, state: pacai.core.gamestate.GameState) -> None:
        """ Update the UI with the current state of the game. """

        pass

    @abc.abstractmethod
    def game_complete(self, final_state: pacai.core.gamestate.GameState) -> None:
        """ Update the UI with the game's final state. """

        pass

    @abc.abstractmethod
    def close(self) -> None:
        """ Close the UI and release all owned resources. """

        pass

    def get_user_input(self) -> UserInputDevice:
        """
        Get an object that conveys user input (in the form of actions).
        Not all UIs will support user input.
        """

        raise NotImplementedError(f"This view ('{type(self).__qualname__}') does not support keyboards.")
