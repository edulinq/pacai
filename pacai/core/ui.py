import abc

import pacai.core.gamestate

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
