import logging
import random
import typing

import pacai.core.action
import pacai.core.gamestate
import pacai.gridworld.board
import pacai.gridworld.mdp

AGENT_INDEX: int = 0
""" The fixed index of the only agent. """

AGENT_MARKER: pacai.core.board.Marker = pacai.core.board.MARKER_AGENT_0
""" The fixed marker of the only agent. """

# TODO(eriq) - Arguments (e.g. living reward, noise, etc)

class GameState(pacai.core.gamestate.GameState):
    """ A game state specific to a standard GridWorld game. """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self._win: bool = False
        """ Keep track if the agent exited the game on a winning state. """

    def game_complete(self) -> list[int]:
        # If the agent exited on a positive terminal position, they win.
        if (self._win):
            return [AGENT_INDEX]

        return []

    def process_turn(self,
            action: pacai.core.action.Action,
            rng: random.Random | None = None) -> None:
        if (rng is None):
            logging.warning("No RNG passed to pacai.gridworld.gamestate.GameState.process_turn().")
            rng = random.Random()

        mdp = pacai.gridworld.mdp.GridWorldMDP(self)

        # Get the possible transitions from the MDP.
        transitions = mdp.get_transitions(mdp.get_starting_state(), action)

        # If there are no transitions, the game is over.
        if (len(transitions) == 0):
            self.game_over = True
            return

        # Choose a transition.
        transition = self._choose_transition(transitions, rng)

        # Apply the transition.

        self.score += transition.reward

        old_position = self.get_agent_position(AGENT_INDEX)
        if (old_position is None):
            raise ValueError("GridWorld agent was removed from board.")

        new_position = transition.state.position

        if (old_position != new_position):
            self.board.remove_marker(AGENT_MARKER, old_position)
            self.board.place_marker(AGENT_MARKER, new_position)

        if (transition.state.is_terminal and (transition.reward > 0)):
            self._win = True

        logging.debug("Requested Action: '%s', Actual Action: '%s', Reward: %0.2f.", action, transition.action, transition.reward)

    def _choose_transition(self,
            transitions: list[pacai.core.mdp.Transition],
            rng: random.Random) -> pacai.core.mdp.Transition:
        probability_sum = 0.0
        point = rng.random()

        for transition in transitions:
            probability_sum += transition.probability
            if (probability_sum > 1.0):
                raise ValueError(f"Transition probabilities is over 1.0, found at least {probability_sum}.")

            if (point < probability_sum):
                return transition

        raise ValueError(f"Transition probabilities is less than 1.0, found {probability_sum}.")

    def to_dict(self) -> dict[str, typing.Any]:
        data = super().to_dict()
        data['_win'] = self._win
        return data

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        game_state = super().from_dict(data)
        game_state._win = data['_win']
        return game_state
