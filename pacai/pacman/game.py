import abc
import random

import pacai.core.action
import pacai.core.board
import pacai.core.game
import pacai.core.gamestate
import pacai.pacman.gamestate

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

    @abc.abstractmethod
    def process_action(self, state: pacai.core.gamestate.GameState, action_record: pacai.core.action.ActionRecord) -> pacai.core.gamestate.GameState:
        if (action_record.action not in state.get_legal_actions()):
            raise ValueError(f"Illegal action: '{action_record.action}")

        if (state.agent_index == PACMAN_AGENT_INDEX):
            self._process_pacman_action(state, action_record.action)
        else:
            self._process_ghost_action(state, action_record.action)

        # TEST - update timers

        # TEST
        return state

    @abc.abstractmethod
    def check_end(self, state: pacai.core.gamestate.GameState) -> bool:
        # TEST
        return True

    def _process_pacman_action(self, state: pacai.core.gamestate.GameState, action: pacai.core.action.Action) -> None:
        position = state.get_agent_position()

        """ TEST
        replaced_marker = state.board.move_with_action(position, action_record.action)

        # Check collisions.
        if (replaced_marker == pacai.pacman.board.MARKER_PELLET):
            # Eat a food pellet.
            state.food_count -= 1
            state.score += FOOD_POINTS

            if (state.food_count <= 0):
                state.score += BOARD_CLEAR_POINTS
                state.game_over = True
        elif (replaced_marker == pacai.pacman.board.MARKER_CAPSULE):
            # Eat a power capsule.
            state.power_time = POWER_TIME
        elif (replaced_marker.is_agent()):
            # Interact with a ghost.

            if (state.power_time > 0):
                # The power capsule is active, pacman eats the ghost.
                state.score += GHOST_POINTS
            else:
                # The power capsule is not active, the ghost eats pacman.
                state.score += LOSE_POINTS

                # Replace the ghost on top of pacman.
                state.board.place(position, replaced_marker)

                # Game is over.
                state.game_over = True

        # Pacman always loses a point each turn.
        state.score -= TIME_PENALTY

        if (state.power_time > 0):
            state.power_time -= 1
        """

    def _process_ghost_action(self, state: pacai.core.gamestate.GameState, action: pacai.core.action.Action) -> None:
        position = state.get_agent_position()

        """ TEST
        if (position is None):
            # The ghost is not on the board, it needs to respawn.
            position = state.board.get_agent_initial_position(state.agent_index)

            # Only respawn the ghost if their spawn location is empty.
            if (state.board.is_empty(position)):
                marker = pacai.core.board.Marker(str(state.agent_index))
                self.board.place(position, marker)
        else:
            replaced_marker = state.board.move_with_action(position, action_record.action)

            # TEST - HERE

        # TEST respawn if position is None
        """
