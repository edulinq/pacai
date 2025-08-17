import random
import typing

import PIL.Image

import pacai.core.action
import pacai.core.gamestate
import pacai.core.spritesheet
import pacai.pacman.board

PACMAN_MARKER: pacai.core.board.Marker = pacai.core.board.MARKER_AGENT_0
""" The board marker that Pac-Man always uses. """

SCARED_TIME: int = 40
""" When a Pacman eats a capsule, ghosts get scared for this number of moves. """

SCARED_MOVE_PENALTY: int = 50
""" Ghost speed gets modified by this constant when scared. """

PACMAN_AGENT_INDEX: int = 0
""" Every Pac-Man game should have exactly one Pac-Man agent at this index. """

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
""" Points for cleaning all the food from the board. """

GHOST_POINTS: int = 200
""" Points for eating a ghost. """

LOSE_POINTS: int = -500
""" Points for getting eaten. """

CRASH_POINTS: int = -1000000
""" Points for crashing the game. """

class GameState(pacai.core.gamestate.GameState):
    """ A game state specific to a standard Pacman game. """

    def __init__(self,
            scared_timers: dict[int, int] | None = None,
            **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        if (scared_timers is None):
            scared_timers = {}

        self.scared_timers: dict[int, int] = scared_timers
        """
        When Pac-Man consumes a power pellet, each ghost get's scared for a specific amount of time.
        When a ghost dies their scared timer resets,
        so all ghosts need an independent timer.
        """

    def copy(self) -> pacai.core.gamestate.GameState:
        new_state = super().copy()
        new_state = typing.cast(GameState, new_state)

        new_state.scared_timers = self.scared_timers.copy()

        return new_state

    def process_agent_timeout(self, agent_index: int) -> None:
        # Treat timeouts like crashes.
        self.process_agent_crash(agent_index)

    def process_agent_crash(self, agent_index: int) -> None:
        super().process_agent_crash(agent_index)

        if (agent_index == PACMAN_AGENT_INDEX):
            self.score += CRASH_POINTS

    def is_scared(self, agent_index: int = -1) -> bool:
        """ Check if the given agent (or the current agent) is currently scared. """

        if (agent_index == -1):
            agent_index = self.agent_index

        return ((agent_index in self.scared_timers) and (self.scared_timers[agent_index] > 0))

    def compute_move_delay(self, agent_index: int) -> int:
        move_delay = super().compute_move_delay(agent_index)

        if (self.is_scared(agent_index)):
            move_delay += SCARED_MOVE_PENALTY

        return move_delay

    def get_legal_actions(self, position: pacai.core.board.Position | None = None) -> list[pacai.core.action.Action]:
        actions = super().get_legal_actions(position)

        # Ghosts have special rules for their actions.
        if (self.agent_index > 0):
            self._get_ghost_legal_actions(actions)

        return actions

    def food_count(self) -> int:
        """ Get the count of all food currently on the board. """

        return self.board.get_marker_count(pacai.pacman.board.MARKER_PELLET)

    def get_food(self) -> set[pacai.core.board.Position]:
        """ Get the positions of all food currently on the board. """

        return self.board.get_marker_positions(pacai.pacman.board.MARKER_PELLET)

    def get_ghost_positions(self) -> dict[int, pacai.core.board.Position]:
        """ Get the position of all ghosts currently on the board. """

        ghosts = {}

        for (agent_index, agent_position) in self.get_agent_positions().items():
            if (agent_index == PACMAN_AGENT_INDEX):
                continue

            if (agent_position is None):
                continue

            ghosts[agent_index] = agent_position

        return ghosts

    def get_scared_ghost_positions(self) -> dict[int, pacai.core.board.Position]:
        """ Get the position of all scared ghosts currently on the board. """

        ghosts = self.get_ghost_positions()
        return {index: position for (index, position) in ghosts.items() if self.is_scared(index)}

    def get_nonscared_ghost_positions(self) -> dict[int, pacai.core.board.Position]:
        """ Get the position of all non-scared ghosts currently on the board. """

        ghosts = self.get_ghost_positions()
        return {index: position for (index, position) in ghosts.items() if not self.is_scared(index)}

    def _get_ghost_legal_actions(self, actions: list[pacai.core.action.Action]) -> None:
        """
        Ghosts cannot stop (unless there are no other actions),
        and cannot turn around unless they reach a dead end (but can turn 90 degrees at intersections).
        """

        # Remove stop.
        if (pacai.core.action.STOP in actions):
            actions.remove(pacai.core.action.STOP)

        # Remove going backwards unless there are no other actions.
        last_action = self.get_last_agent_action(self.agent_index)
        reverse_direction = self.get_reverse_action(last_action)
        if ((reverse_direction in actions) and (len(actions) > 1)):
            actions.remove(reverse_direction)

        # If we are not doing anything, then just stop.
        if (len(actions) == 0):
            actions.append(pacai.core.action.STOP)

    def game_complete(self) -> list[int]:
        # Pacman wins if there is no food on the board.
        if (self.food_count() == 0):
            return [PACMAN_AGENT_INDEX]

        # Otherwise, the ghosts (if any) win.
        ghost_indexes = list(self.move_delays.keys())
        ghost_indexes.remove(PACMAN_AGENT_INDEX)

        return ghost_indexes

    def sprite_lookup(self,
            sprite_sheet: pacai.core.spritesheet.SpriteSheet,
            position: pacai.core.board.Position,
            marker: pacai.core.board.Marker | None = None,
            action: pacai.core.action.Action | None = None,
            adjacency: pacai.core.board.AdjacencyString | None = None,
            animation_key: str | None = None,
            ) -> PIL.Image.Image:
        # If the ghost is scared, swap the marker.
        if ((marker is not None)
                and (marker.is_agent())
                and (marker != PACMAN_MARKER)
                and (self.is_scared(marker.get_agent_index()))):
            marker = pacai.pacman.board.MARKER_SCARED_GHOST

        return super().sprite_lookup(sprite_sheet, position, marker = marker, action = action, adjacency = adjacency, animation_key = animation_key)

    def process_turn(self,
            action: pacai.core.action.Action,
            rng: random.Random | None = None,
            **kwargs: typing.Any) -> None:
        # Do actions specific to Pac-Man or ghosts.
        if (self.agent_index == PACMAN_AGENT_INDEX):
            self._process_pacman_turn(action)
        else:
            self._process_ghost_turn(action)

    def _process_pacman_turn(self, action: pacai.core.action.Action) -> None:
        """
        Process Pac-Man-specific interactions for a turn.
        """

        agent_marker = pacai.core.board.Marker(str(self.agent_index))

        # Compute the agent's new position.
        old_position = self.get_agent_position()
        if (old_position is None):
            raise ValueError("Pacman cannot make a move when they are not on the board.")

        new_position = old_position.apply_action(action)

        # Get all the markers that we are moving into.
        interaction_markers = set()
        if (old_position != new_position):
            interaction_markers = self.board.get(new_position)

            # Since we are moving, pickup the agent from their current location.
            self.board.remove_marker(agent_marker, old_position)

        died = False

        # Process actions for all the markers we are moving onto.
        for interaction_marker in interaction_markers:
            if (interaction_marker == pacai.pacman.board.MARKER_PELLET):
                # Eat a food pellet.
                self.board.remove_marker(interaction_marker, new_position)
                self.score += FOOD_POINTS

                if (self.food_count() == 0):
                    self.score += BOARD_CLEAR_POINTS
                    self.game_over = True
            elif (interaction_marker == pacai.pacman.board.MARKER_CAPSULE):
                # Eat a power capsule, scare all ghosts.
                self.board.remove_marker(interaction_marker, new_position)

                # Scare all ghosts.
                for agent_index in self.move_delays.keys():
                    if (agent_index == PACMAN_AGENT_INDEX):
                        continue

                    self.scared_timers[agent_index] = SCARED_TIME
            elif (interaction_marker.is_agent()):
                # Interact with a ghost.

                if (self.is_scared(interaction_marker.get_agent_index())):
                    # The ghost is scared, Pac-Man eats the ghost.
                    self._kill_ghost(interaction_marker.get_agent_index())
                    self.board.remove_marker(interaction_marker, new_position)
                else:
                    # The ghost is not scared, the ghost eats Pac-Man.
                    self.score += LOSE_POINTS
                    died = True

                    # Game is over.
                    self.game_over = True

        # Move the agent to the new location if it did not die.
        if (not died):
            self.board.place_marker(agent_marker, new_position)

        # Pacman always loses a point each turn.
        self.score -= TIME_PENALTY

    def _process_ghost_turn(self, action: pacai.core.action.Action) -> None:
        """
        Process ghost-specific interactions for a turn.
        """

        agent_marker = pacai.core.board.Marker(str(self.agent_index))

        # Compute the agent's new position.
        old_position = self.get_agent_position()
        if (old_position is None):
            # The ghost is currently dead and needs to respawn.
            new_position = self.board.get_agent_initial_position(self.agent_index)
            if (new_position is None):
                raise ValueError(f"Cannot find initial position for ghost (agent {self.agent_index}).")
        else:
            new_position = old_position.apply_action(action)

        # Get all the markers that we are moving into.
        interaction_markers = set()
        if (old_position != new_position):
            interaction_markers = self.board.get(new_position)

            # Since we are moving, pickup the agent from their current location.
            if (old_position is not None):
                self.board.remove_marker(agent_marker, old_position)

        died = False

        # Process actions for all the markers we are moving onto.
        for interaction_marker in interaction_markers:
            if (interaction_marker == PACMAN_MARKER):
                # Interact with Pac-Man.

                if (self.is_scared()):
                    # The ghost is scared, Pac-Man eats the ghost.
                    self._kill_ghost(self.agent_index)
                    died = True
                else:
                    # The ghost is not scared, the ghost eats Pac-Man.
                    self.score += LOSE_POINTS
                    self.board.remove_marker(interaction_marker, new_position)

                    # Game is over.
                    self.game_over = True

        # Move the agent to the new location if it did not die.
        if (not died):
            self.board.place_marker(agent_marker, new_position)

        # Decrement the scared timer.
        if (self.agent_index in self.scared_timers):
            self.scared_timers[self.agent_index] -= 1

            if (self.scared_timers[self.agent_index] <= 0):
                self._stop_scared(self.agent_index)

    def _kill_ghost(self, agent_index: int) -> None:
        """ Set the non-board state for killing a ghost. """

        # Add points.
        self.score += GHOST_POINTS

        # Reset the last action.
        if (agent_index not in self.agent_actions):
            self.agent_actions[agent_index] = []

        self.agent_actions[agent_index].append(pacai.core.action.STOP)

        # The ghost is no longer scared.
        self._stop_scared(agent_index)

    def _stop_scared(self, agent_index: int) -> None:
        """ Stop a ghost from being scared. """

        # Reset the scared timer.
        if (agent_index in self.scared_timers):
            del self.scared_timers[agent_index]
