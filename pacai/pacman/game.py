import abc
import random
import typing

import pacai.core.action
import pacai.core.board
import pacai.core.game
import pacai.core.gamestate
import pacai.pacman.gamestate

PACMAN_MARKER: pacai.core.board.Marker = pacai.core.board.MARKER_AGENT_0

SCARED_TIME: int = 40
""" When a Pacman eats a capsule, ghosts get scared for this number of moves. """

SCARED_MOVE_PENALTY: int = 50
""" Ghost speed gets modified by this constant when scared. """

PACMAN_AGENT_INDEX: int = 0
""" Every pacman game should have exactly one pacman agent at this index. """

FIRST_GHOST_AGENT_INDEX: int = 1
"""
Ghost indexes start here.
This value may just be used as a placeholder to represent the "ghost team".
"""

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

    def game_complete(self, state: pacai.core.gamestate.GameState, result: pacai.core.game.GameResult) -> None:
        state = typing.cast(pacai.pacman.gamestate.GameState, state)
        if (state.food_count == 0):
            result.winning_agent_index = PACMAN_AGENT_INDEX
        else:
            result.winning_agent_index = FIRST_GHOST_AGENT_INDEX

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
                # Eat a power capsule, scare all ghosts.
                state.board.remove_marker(interaction_marker, new_position)

                # Scare all ghosts.
                for (agent_index, agent_args) in self._agent_args.items():
                    if (agent_index == PACMAN_AGENT_INDEX):
                        continue

                    state.scared_timers[agent_index] = SCARED_TIME
                    agent_args.move_delay += SCARED_MOVE_PENALTY
            elif (interaction_marker.is_agent()):
                # Interact with a ghost.

                if (state.is_scared(interaction_marker.get_agent_index())):
                    # The ghost is scared, pacman eats the ghost.
                    self._kill_ghost(state, interaction_marker.get_agent_index())
                    state.board.remove_marker(interaction_marker, new_position)
                else:
                    # The ghost is not scared, the ghost eats pacman.
                    state.score += LOSE_POINTS
                    died = True

                    # Game is over.
                    state.game_over = True

        # Move the agent to the new location if it did not die.
        if (not died):
            state.board.place_marker(agent_marker, new_position)

        # Pacman always loses a point each turn.
        state.score -= TIME_PENALTY

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

                if (state.is_scared()):
                    # The ghost is scared, pacman eats the ghost.
                    self._kill_ghost(state, state.agent_index)
                    died = True
                else:
                    # The ghost is not scared, the ghost eats pacman.
                    state.score += LOSE_POINTS
                    state.board.remove_marker(interaction_marker, new_position)

                    # Game is over.
                    state.game_over = True

        # Move the agent to the new location if it did not die.
        if (not died):
            state.board.place_marker(agent_marker, new_position)

        # Decrement the scared timer.
        if (state.agent_index in state.scared_timers):
            state.scared_timers[state.agent_index] -= 1

            if (state.scared_timers[state.agent_index] <= 0):
                self._stop_scared(state, state.agent_index)

    def _kill_ghost(self, state: pacai.pacman.gamestate.GameState, agent_index: int) -> None:
        """ Set the non-board state for killing a ghost. """

        # Add points.
        state.score += GHOST_POINTS

        # Reset the last action.
        state.last_agent_actions[agent_index] = pacai.core.action.STOP

        # The ghost is no longer scared.
        self._stop_scared(state, agent_index)

    def _stop_scared(self, state: pacai.pacman.gamestate.GameState, agent_index: int) -> None:
        """ Stop a ghost from being scared. """

        # Reset the scared timer.
        if (agent_index in state.scared_timers):
            del state.scared_timers[agent_index]

        # Reset speed.
        self._agent_args[agent_index].move_delay -= SCARED_MOVE_PENALTY
