import abc
import random
import typing

import pacai.core.action
import pacai.core.board
import pacai.core.game
import pacai.core.gamestate
import pacai.pacman.gamestate

# TODO(eriq): Handle ghost scarred speed (halved).

PACMAN_MARKER: pacai.core.board.Marker = pacai.core.board.MARKER_AGENT_0

POWER_TIME: int = 40
""" When a Pacman eats a capsule, they are powered up for this number of moves. """

PACMAN_AGENT_INDEX: int = 0
""" Every pacman game should have exactly one pacman agent at this index. """

TIME_PENALTY: int = 1
""" Number of points lost each round. """

FOOD_POINTS: int = 10
""" Points for eating food. """

BOARD_CLEAR_POINTS: int = 500
""" Points for clearning all the food from the board. """

GHOST_POINTS: int = 200
""" Points for eating a ghost. """

LOSE_POINTS: int = -500
""" Points for getting eatten. """

class Game(pacai.core.game.Game):
    """
    A game following the standard rules of PacMan.
    """

    def get_initial_state(self, rng: random.Random, board: pacai.core.board.Board) -> pacai.core.gamestate.GameState:
        state = pacai.pacman.gamestate.GameState(board = board)

        state.food_count = len(state.board.get_marker_positions(pacai.pacman.board.MARKER_PELLET))

        return state

    def process_action(self, state: pacai.core.gamestate.GameState, action_record: pacai.core.action.ActionRecord) -> pacai.core.gamestate.GameState:
        if (action_record.action not in state.get_legal_actions()):
            raise ValueError(f"Illegal action for agent {state.agent_index}: '{action_record.action}'.")

        state = typing.cast(pacai.pacman.gamestate.GameState, state)

        # Do actions specific to pacman/ghosts.
        if (state.agent_index == PACMAN_AGENT_INDEX):
            self._process_pacman_turn(state, action_record.action)
        else:
            self._process_ghost_turn(state, action_record.action)

        return state

    def _process_pacman_turn(self, state: pacai.pacman.gamestate.GameState, action: pacai.core.action.Action) -> None:
        """
        Process pacman-specific interactions for a turn.
        """

        agent_marker = pacai.core.board.Marker(str(state.agent_index))

        # Compute the agent's new position.
        old_position = state.get_agent_position()
        if (old_position is None):
            raise ValueError("Pacman cannot make a move when they are not on the board.")

        new_position = old_position.apply_action(action)

        # Get all the markers that we are moving into.
        interaction_markers = set()
        if (old_position != new_position):
            interaction_markers = state.board.get(new_position)

            # Since we are moving, pickup the agent from their current location.
            state.board.remove_marker(agent_marker, old_position)

        died = False

        # Process actions for all the markers we are moving onto.
        for interaction_marker in interaction_markers:
            if (interaction_marker == pacai.pacman.board.MARKER_PELLET):
                # Eat a food pellet.
                state.board.remove_marker(interaction_marker, new_position)

                state.food_count -= 1
                state.score += FOOD_POINTS

                if (state.food_count <= 0):
                    state.score += BOARD_CLEAR_POINTS
                    state.game_over = True
            elif (interaction_marker == pacai.pacman.board.MARKER_CAPSULE):
                # Eat a power capsule.
                state.board.remove_marker(interaction_marker, new_position)
                state.power_time = POWER_TIME
            elif (interaction_marker.is_agent()):
                # Interact with a ghost.

                if (state.power_time > 0):
                    # The power capsule is active, pacman eats the ghost.
                    state.board.remove_marker(interaction_marker, new_position)
                    state.score += GHOST_POINTS
                else:
                    # The power capsule is not active, the ghost eats pacman.
                    state.score += LOSE_POINTS
                    died = True

                    # Game is over.
                    state.game_over = True

        # Move the agent to the new location if it did not die.
        if (not died):
            state.board.place_marker(agent_marker, new_position)

        # Pacman always loses a point each turn.
        state.score -= TIME_PENALTY

        # Decrement the power timer.
        if (state.power_time > 0):
            state.power_time -= 1

    def _process_ghost_turn(self, state: pacai.pacman.gamestate.GameState, action: pacai.core.action.Action) -> None:
        """
        Process ghost-specific interactions for a turn.
        """

        agent_marker = pacai.core.board.Marker(str(state.agent_index))

        # Compute the agent's new position.
        old_position = state.get_agent_position()
        if (old_position is None):
            # The ghost is currently dead and needs to respawn.
            new_position = state.board.get_agent_initial_position(state.agent_index)
            if (new_position is None):
                raise ValueError(f"Cannot find initial position for ghost (agent {state.agent_index}).")
        else:
            new_position = old_position.apply_action(action)

        # Get all the markers that we are moving into.
        interaction_markers = set()
        if (old_position != new_position):
            interaction_markers = state.board.get(new_position)

            # Since we are moving, pickup the agent from their current location.
            if (old_position is not None):
                state.board.remove_marker(agent_marker, old_position)

        died = False

        # Process actions for all the markers we are moving onto.
        for interaction_marker in interaction_markers:
            if (interaction_marker == PACMAN_MARKER):
                # Interact with pacman.

                if (state.power_time > 0):
                    # The power capsule is active, pacman eats the ghost.
                    state.score += GHOST_POINTS
                    died = True
                else:
                    # The power capsule is not active, the ghost eats pacman.
                    state.score += LOSE_POINTS
                    state.board.remove_marker(interaction_marker, new_position)

                    # Game is over.
                    state.game_over = True

        # Move the agent to the new location if it did not die.
        if (not died):
            state.board.place_marker(agent_marker, new_position)
