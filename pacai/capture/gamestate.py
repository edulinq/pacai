# TEST
import random

import PIL.Image

import pacai.core.action
import pacai.core.gamestate
import pacai.core.spritesheet
import pacai.pacman.board
import pacai.pacman.gamestate

TEAM_MODIFIERS: tuple[int, int] = (-1, 1)
""" The different modifiers for the two teams: evens/west and odds/east. """

FOOD_POINTS: int = 10
""" Points for eating food. """

KILL_GHOST_POINTS: int = 0
""" Points for eating a scared ghost. """

KILL_PACMAN_POINTS: int = 0
""" Points for eating a Pac-Man. """

class GameState(pacai.pacman.gamestate.GameState):
    """
    A game state specific to a game of Capture.
    Derived from the Pac-Man game state.

    A common concept in this game is that the board is divided in half between two teams.
    The even team (with even agent indexes) start in the west and uses a -1 modifier.
    The odd team (with odd agent indexes) start in the east and uses a +1 modifier.
    """

    def _team_modifier(self, agent_index: int = -1) -> int:
        """ Return -1 or +1 depending on if the even or odd team (respectively) is currently active. """

        if (agent_index == -1):
            agent_index = self.agent_index

        return ((agent_index % 2) * 2) - 1

    def _team_side(self, agent_index: int = -1, position: pacai.core.board.Position | None = None) -> int:
        """
        Return -1 or +1 depending on which side of the board this position is on.
        If no position is provided, the agent's position will be used.
        If no agent index is provided, the current agent index will be used.
        """

        if (position is None):
            if (agent_index == -1):
                agent_index = self.agent_index

            position = self.get_agent_position(agent_index = agent_index)

        if (position is None):
            raise ValueError("Could not find position.")

        if (position.row < (self.board.width / 2)):
            return -1

        return 1

    def _team_agent_indexes(self, team_modifier: int) -> list[int]:
        """ Get the agent indexes for the current team. """

        return [agent_index for agent_index in self.get_agent_indexes() if (self._team_modifier(agent_index) == team_modifier)]

    def is_scared(self, agent_index: int = -1) -> bool:
        # Agents cannot be scared when on the opponent's side of the board.
        if (self._team_side(agent_index = agent_index) != self._team_modifier(agent_index = agent_index)):
            return False

        return super().is_scared(agent_index = agent_index)

    def process_agent_crash(self, agent_index: int):
        super().process_agent_crash(agent_index)

        # Set the score in favor of the non-crashing team.
        self.score = -1 * self._team_modifier(agent_index) * pacai.pacman.gamestate.CRASH_POINTS

    def get_legal_actions(self, position: pacai.core.board.Position | None = None) -> list[pacai.core.action.Action]:
        if (position is None):
            position = self.get_agent_position(self.agent_index)

        # Dead agents (agents not on the board) can only stop (when they will respawn).
        if (position is None):
            return [pacai.core.action.STOP]

        return super().get_legal_actions(position)

    def food_count(self, team_modifier: int = 0, agent_index: int = -1) -> int:
        """
        Get the count of all food currently on the board for the specified team.
        If no team is specified, use the given agent's team.
        If no agent is specified, use the current agent.
        """

        return len(self.get_food(team_modifier = team_modifier, agent_index = agent_index))

    def get_food(self, team_modifier: int = 0, agent_index: int = -1) -> set[pacai.core.board.Position]:
        """
        Get the positions of all food currently on the board for the specific team.
        This refers to food that the given team can eat (which lives on the opponents side).
        If no team is specified, use the given agent's team.
        If no agent is specified, use the current agent.
        """

        if (team_modifier == 0):
            if (agent_index == -1):
                agent_index = self.agent_index

            team_modifier = self._team_modifier(agent_index)

        team_food = set()
        for position in self.board.get_marker_positions(pacai.pacman.board.MARKER_PELLET):
            # If the food does not belong to this team, they can eat it.
            if (self._team_side(position = position) != team_modifier):
                team_food.add(position)

        return team_food

    def get_team_positions(self, team_modifier: int) -> dict[int, pacai.core.board.Position]:
        """ Get the position of all agents on the board belonging to the given team. """

        agents = {}

        for (agent_index, agent_position) in self.get_agent_positions().items():
            if (team_modifier != self._team_modifier(agent_index)):
                continue

            if (agent_position is None):
                continue

            agents[agent_index] = agent_position

        return agents

    def get_ally_positions(self, agent_index: int = -1) -> dict[int, pacai.core.board.Position]:
        """ Get the position of all allies currently on the board. """

        if (agent_index == -1):
            agent_index = self.agent_index

        team_modifier = self._team_modifier(agent_index)

        agents = self.get_team_positions(team_modifier)

        # Remove self.
        agents.pop(agent_index, None)

        return agents

    def get_scared_ally_positions(self) -> dict[int, pacai.core.board.Position]:
        """ Get the position of all scared allies currently on the board. """

        allies = self.get_ally_positions()
        return {index: position for (index, position) in allies.items() if self.is_scared(index)}

    def get_nonscared_ally_positions(self) -> dict[int, pacai.core.board.Position]:
        """ Get the position of all non-scared allies currently on the board. """

        allies = self.get_ally_positions()
        return {index: position for (index, position) in allies.items() if not self.is_scared(index)}

    def get_opponent_positions(self, agent_index: int = -1) -> dict[int, pacai.core.board.Position]:
        """ Get the position of all opponents currently on the board. """

        if (agent_index == -1):
            agent_index = self.agent_index

        team_modifier = self._team_modifier(agent_index)

        return self.get_team_positions(-team_modifier)

    def get_scared_opponent_positions(self) -> dict[int, pacai.core.board.Position]:
        """ Get the position of all scared opponents currently on the board. """

        opponents = self.get_opponent_positions()
        return {index: position for (index, position) in opponents.items() if self.is_scared(index)}

    def get_nonscared_opponent_positions(self) -> dict[int, pacai.core.board.Position]:
        """ Get the position of all non-scared opponents currently on the board. """

        opponents = self.get_opponent_positions()
        return {index: position for (index, position) in opponents.items() if not self.is_scared(index)}

    def game_complete(self) -> list[int]:
        # A side wins if there is no food left for them to eat.
        for team_modifier in TEAM_MODIFIERS:
            if (self.food_count(team_modifier = team_modifier) == 0):
                return self._team_agent_indexes(team_modifier)

        return []

    # TEST
    def sprite_lookup(self,
            sprite_sheet: pacai.core.spritesheet.SpriteSheet,
            position: pacai.core.board.Position,
            marker: pacai.core.board.Marker | None = None,
            action: pacai.core.action.Action | None = None,
            adjacency: pacai.core.board.AdjacencyString | None = None,
            animation_key: str | None = None,
            ) -> PIL.Image.Image:
        # TEST - Modify food, walls.

        ''' TEST
        # If the ghost is scared, swap the marker.
        if ((marker is not None)
                and (marker.is_agent())
                and (marker != PACMAN_MARKER)
                and (self.is_scared(marker.get_agent_index()))):
            marker = SCARED_GHOST_MARKER
        '''

        return super().sprite_lookup(sprite_sheet, position, marker = marker, action = action, adjacency = adjacency, animation_key = animation_key)

    def process_turn(self,  # pylint: disable=too-many-statements
            action: pacai.core.action.Action,
            rng: random.Random | None = None,
            **kwargs) -> None:
        agent_marker = pacai.core.board.Marker(str(self.agent_index))
        team_modifier = self._team_modifier()

        # Compute the agent's new position.
        old_position = self.get_agent_position()
        if (old_position is None):
            # The agent is currently dead and needs to respawn.
            new_position = self.board.get_agent_initial_position(self.agent_index)
            if (new_position is None):
                raise ValueError(f"Cannot find initial position for agent {self.agent_index}.")
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
            if (interaction_marker == pacai.pacman.board.MARKER_PELLET):
                # Eat a food pellet.
                self.board.remove_marker(interaction_marker, new_position)
                self.score += team_modifier * FOOD_POINTS

                if (self.food_count(team_modifier = team_modifier) == 0):
                    self.game_over = True
            elif (interaction_marker == pacai.pacman.board.MARKER_CAPSULE):
                # Eat a power capsule, scare all enemy ghosts.
                self.board.remove_marker(interaction_marker, new_position)

                # Scare all enemies.
                for agent_index in self._team_agent_indexes(-team_modifier):
                    self.scared_timers[agent_index] = pacai.pacman.gamestate.SCARED_TIME
            elif (interaction_marker.is_agent()):
                other_agent_index = interaction_marker.get_agent_index()
                other_team_modifier = self._team_modifier(other_agent_index)

                if (team_modifier == other_team_modifier):
                    # This is an agent on our team, nothing to do.
                    continue

                # Check if anyone is scared.
                self_scared = self.is_scared(agent_index)
                other_scared = self.is_scared(other_agent_index)

                # Check who is a ghost (agent's on their own side are a ghost).
                # We know if we are a ghost if the other agent is a ghost or scared.
                other_ghost = (other_team_modifier == self._team_side(agent_index = other_agent_index))

                # Check who was eaten (and remove them), what team did the eating, and the points that should be awarded.
                eating_team_modifier = 0
                points = 0

                if (self_scared or other_ghost):
                    # We got eaten, but our marker is already off the board.
                    died = True
                    self._kill_agent(agent_index)

                    eating_team_modifier = other_team_modifier

                    if (self_scared):
                        points = KILL_GHOST_POINTS
                    else:
                        points = KILL_PACMAN_POINTS
                else:
                    # If we ate the opponent, remove them from the board.
                    self.board.remove_marker(interaction_marker, new_position)
                    self._kill_agent(other_agent_index)

                    eating_team_modifier = team_modifier

                    if (other_scared):
                        points = KILL_GHOST_POINTS
                    else:
                        points = KILL_PACMAN_POINTS

                self.score += (eating_team_modifier * points)

        # Move the agent to the new location if it did not die.
        if (not died):
            self.board.place_marker(agent_marker, new_position)

        # Decrement the scared timer.
        if (self.agent_index in self.scared_timers):
            self.scared_timers[self.agent_index] -= 1

            if (self.scared_timers[self.agent_index] <= 0):
                self._stop_scared(self.agent_index)

    def _kill_agent(self, agent_index: int) -> None:
        """ Set the non-board state for killing an agent. """

        # Reset the last action.
        if (agent_index not in self.agent_actions):
            self.agent_actions[agent_index] = []

        self.agent_actions[agent_index].append(pacai.core.action.STOP)

        # The agent is no longer scared.
        self._stop_scared(agent_index)

    def _stop_scared(self, agent_index: int) -> None:
        """ Stop an agent from being scared. """

        if (agent_index in self.scared_timers):
            del self.scared_timers[agent_index]
