import typing

import pacai.core.action
import pacai.core.board
import pacai.core.gamestate
import pacai.core.mdp
import pacai.gridworld.board

DEFAULT_NOISE: float = 0.2
DEFAULT_LIVING_REWARD: float = 0.0

POSSIBLE_STATE_MARKERS: set[pacai.core.board.Marker] = {
    pacai.gridworld.board.AGENT_MARKER,
    pacai.gridworld.board.MARKER_TERMINAL,
}
""" The possible markers that can be in MDP states. """

class GridWorldMDP(pacai.core.mdp.MarkovDecisionProcess[pacai.core.mdp.MDPStatePosition]):
    """ An MDP that represents the GridWorld game. """

    def __init__(self,
            start_position: pacai.core.board.Position | None = None,
            noise: float = DEFAULT_NOISE,
            living_reward: float = DEFAULT_LIVING_REWARD,
            **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        self.board: pacai.gridworld.board.Board | None = None
        """ The board this MDP is operating on. """

        self.start_position: pacai.core.board.Position | None = start_position
        """ The position to start from. """

        self.noise = noise
        """ How often actions result in unintended consequences. """

        self.living_reward: float = living_reward
        """ The reward for living for a time step (action). """

    def game_start(self, initial_game_state: pacai.core.gamestate.GameState) -> None:
        self.board = typing.cast(pacai.gridworld.board.Board, initial_game_state.board)

        if (self.start_position is None):
            self.start_position = initial_game_state.get_agent_position()

        if (self.start_position is None):
            raise ValueError("Could not find starting position.")

    def get_starting_state(self) -> pacai.core.mdp.MDPStatePosition:
        if (self.start_position is None):
            raise ValueError("GridWorld MDP as not been initialized via game_start().")

        return pacai.core.mdp.MDPStatePosition(self.start_position)

    def get_states(self) -> list[pacai.core.mdp.MDPStatePosition]:
        if (self.board is None):
            raise ValueError("GridWorld MDP as not been initialized via game_start().")

        # Start with the terminal state.
        states = [pacai.core.mdp.MDPStatePosition(pacai.core.mdp.TERMINAL_POSITION)]

        # Possible positions can only have at certain set of markers.
        for row in range(self.board._original_height):
            for col in range(self.board._original_width):
                position = pacai.core.board.Position(row, col)
                if (self.board.is_wall(position)):
                    continue

                markers = self.board.get(position)
                if (not markers.issubset(POSSIBLE_STATE_MARKERS)):
                    continue

                states.append(pacai.core.mdp.MDPStatePosition(position))

        return states

    def is_terminal_state(self, state: pacai.core.mdp.MDPStatePosition) -> bool:
        return state.is_terminal()

    def get_possible_actions(self, state: pacai.core.mdp.MDPStatePosition) -> list[pacai.core.action.Action]:
        """
        There are special rules for actions in GridWorld.

        If you are on the true terminal state, [STOP] should be returned.
        If you are on a state that transitions to the true terminal state, you can exit.
        Otherwise, you can try to move in all cardinal direction (even into walls),
        or just stop (stay still).
        """

        if (self.board is None):
            raise ValueError("GridWorld MDP as not been initialized via game_start().")

        # True terminal states can only stop.
        if (self.is_terminal_state(state)):
            return [pacai.core.action.STOP]

        # Positions with scores transition to the true terminal.
        if (self.board.is_terminal_position(state.position)):
            return [pacai.core.mdp.ACTION_EXIT]

        # All other states can try moving in any cardinal direction.
        return list(pacai.core.board.CARDINAL_OFFSETS.keys())

    def get_transitions(self, state: pacai.core.mdp.MDPStatePosition, action: pacai.core.action.Action) -> list[pacai.core.mdp.Transition]:
        """
        In GridWorld, you may not move in the direction you are intending.

        Agents that are stopped (taking the STOP action) will not move or gain any rewards.

        You have a (1.0 - noise) chance of moving in the desired direction,
        and a (noise / 2) chance of moving to the left or right of your intended direction.
        You cannot move into a wall, but you can "bump" against a wall (causing you not to move).
        """

        if (self.board is None):
            raise ValueError("GridWorld MDP as not been initialized via game_start().")

        # True terminal states are done.
        if (self.is_terminal_state(state)):
            return []

        # Positions with values will always transition to the true terminal state.
        if (self.board.is_terminal_position(state.position)):
            mdp_state = pacai.core.mdp.MDPStatePosition(pacai.core.mdp.TERMINAL_POSITION)
            return [pacai.core.mdp.Transition(mdp_state, pacai.core.mdp.ACTION_EXIT, 1.0, 0.0)]

        # Stopped agents always just sit there.
        if (action == pacai.core.action.STOP):
            return [pacai.core.mdp.Transition(state, action, 1.0, 0.0)]

        possible_actions = self.get_possible_actions(state)
        if (action not in possible_actions):
            raise ValueError(f"Got an illegal action '{action}'. Available actions are: {possible_actions}.")

        (north_state, east_state, south_state, west_state) = self._get_move_states(state)  # pylint: disable=unbalanced-tuple-unpacking

        transitions = []

        if (action == pacai.core.action.NORTH):
            transitions.append(pacai.core.mdp.Transition(north_state, pacai.core.action.NORTH, (1.0 - self.noise), self._get_reward(north_state)))
            transitions.append(pacai.core.mdp.Transition(east_state, pacai.core.action.EAST, (self.noise / 2.0), self._get_reward(east_state)))
            transitions.append(pacai.core.mdp.Transition(west_state, pacai.core.action.WEST, (self.noise / 2.0), self._get_reward(west_state)))
        elif (action == pacai.core.action.EAST):
            transitions.append(pacai.core.mdp.Transition(east_state, pacai.core.action.EAST, (1.0 - self.noise), self._get_reward(east_state)))
            transitions.append(pacai.core.mdp.Transition(north_state, pacai.core.action.NORTH, (self.noise / 2.0), self._get_reward(north_state)))
            transitions.append(pacai.core.mdp.Transition(south_state, pacai.core.action.SOUTH, (self.noise / 2.0), self._get_reward(south_state)))
        elif (action == pacai.core.action.SOUTH):
            transitions.append(pacai.core.mdp.Transition(south_state, pacai.core.action.SOUTH, (1.0 - self.noise), self._get_reward(south_state)))
            transitions.append(pacai.core.mdp.Transition(east_state, pacai.core.action.EAST, (self.noise / 2.0), self._get_reward(east_state)))
            transitions.append(pacai.core.mdp.Transition(west_state, pacai.core.action.WEST, (self.noise / 2.0), self._get_reward(west_state)))
        elif (action == pacai.core.action.WEST):
            transitions.append(pacai.core.mdp.Transition(west_state, pacai.core.action.WEST, (1.0 - self.noise), self._get_reward(west_state)))
            transitions.append(pacai.core.mdp.Transition(north_state, pacai.core.action.NORTH, (self.noise / 2.0), self._get_reward(north_state)))
            transitions.append(pacai.core.mdp.Transition(south_state, pacai.core.action.SOUTH, (self.noise / 2.0), self._get_reward(south_state)))
        else:
            raise ValueError(f"Unknown action: '{action}'.")

        # Because of bonking against walls, we may have multiple transitions pointing to the same state.
        # Merge them and return the results.
        return self._merge_transitions(transitions)

    def _merge_transitions(self, transitions: list[pacai.core.mdp.Transition]) -> list[pacai.core.mdp.Transition]:
        """ Merge transitions that are pointing to the same state together. """

        merged: dict[pacai.core.mdp.MDPStatePosition, pacai.core.mdp.Transition] = {}
        for transition in transitions:
            if (transition.state in merged):
                merged[transition.state].update(transition)
            else:
                merged[transition.state] = transition

        return list(merged.values())

    def _get_reward(self, state: pacai.core.mdp.MDPStatePosition) -> float:
        if (self.board is None):
            raise ValueError("GridWorld MDP as not been initialized via game_start().")

        if (self.board.is_terminal_position(state.position)):
            return self.board.get_terminal_value(state.position)

        return self.living_reward

    def _get_move_states(self,
            state: pacai.core.mdp.MDPStatePosition,
            ) -> tuple[
                pacai.core.mdp.MDPStatePosition, pacai.core.mdp.MDPStatePosition,
                pacai.core.mdp.MDPStatePosition, pacai.core.mdp.MDPStatePosition]:
        """
        Get the positions an agent could move to.
        If a move would put the agent into a wall, they will "bonk" the wall and not move.

        Positions are returned in NESW order.
        """

        if (self.board is None):
            raise ValueError("GridWorld MDP as not been initialized via game_start().")

        states = []

        # CARDINAL_OFFSETS is in NESW order.
        for offset in pacai.core.board.CARDINAL_OFFSETS.values():
            new_position = state.position.add(offset)

            if (self.board.is_wall(new_position)):
                states.append(state)
            else:
                states.append(pacai.core.mdp.MDPStatePosition(new_position))

        return tuple(states)  # type: ignore[return-value]

    def to_dict(self) -> dict[str, typing.Any]:
        data = super().to_dict()

        if (self.board is not None):
            data['board'] = self.board.to_dict()

        return data

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        mdp = super().from_dict(data)

        if ('board' in data):
            mdp.board = pacai.gridworld.board.Board.from_dict(data['board'])

        return mdp
