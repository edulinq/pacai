import logging
import math
import random
import typing

import PIL.Image
import PIL.ImageDraw

import pacai.core.action
import pacai.core.agentaction
import pacai.core.gamestate
import pacai.core.board
import pacai.core.font
import pacai.core.spritesheet
import pacai.gridworld.board
import pacai.gridworld.mdp

AGENT_INDEX: int = 0
""" The fixed index of the only agent. """

QVALUE_TRIANGLE_POINT_OFFSETS: list[tuple[tuple[float, float], tuple[float, float], tuple[float, float]]] = [
    ((0.0, 0.0), (1.0, 0.0), (0.5, 0.5)),
    ((1.0, 0.0), (1.0, 1.0), (0.5, 0.5)),
    ((1.0, 1.0), (0.0, 1.0), (0.5, 0.5)),
    ((0.0, 1.0), (0.0, 0.0), (0.5, 0.5)),
]
"""
Offsets (as position dimensions) of the points for Q-Value triangles.
Indexes line up with pacai.core.action.CARDINAL_DIRECTIONS.
"""

TRIANGLE_WIDTH: int = 1
""" Width of the Q-Value triangle borders. """

class GameState(pacai.core.gamestate.GameState):
    """ A game state specific to a standard GridWorld game. """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self._win: bool = False
        """ Keep track if the agent exited the game on a winning state. """

        self._mdp_state_values: dict[pacai.gridworld.mdp.GridWorldMDPState, float] = {}
        """
        The MDP state values computed by the agent.
        This member will not be serialized.
        """

        self._qvalues: dict[pacai.gridworld.mdp.GridWorldMDPState, dict[pacai.core.action.Action, float]] = {}
        """
        The Q-values computed by the agent.
        This member will not be serialized.
        """

    def agents_game_start(self, agent_responses: dict[int, pacai.core.agentaction.AgentActionRecord]) -> None:
        if (AGENT_INDEX not in agent_responses):
            return

        agent_action = agent_responses[AGENT_INDEX].agent_action
        if (agent_action is None):
            return

        if ('mdp_state_values' in agent_action.other_info):
            for (raw_position, value) in agent_action.other_info['mdp_state_values']:
                position = pacai.core.board.Position.from_dict(raw_position)
                self._mdp_state_values[pacai.gridworld.mdp.GridWorldMDPState(position)] = value

        if ('qvalues' in agent_action.other_info):
            for (raw_position, raw_action, qvalue) in agent_action.other_info['qvalues']:
                position = pacai.core.board.Position.from_dict(raw_position)
                action = pacai.core.action.Action(raw_action)
                mdp_state = pacai.gridworld.mdp.GridWorldMDPState(position)

                if (mdp_state not in self._qvalues):
                    self._qvalues[mdp_state] = {}

                self._qvalues[mdp_state][action] = qvalue

    def game_complete(self) -> list[int]:
        # If the agent exited on a positive terminal position, they win.
        if (self._win):
            return [AGENT_INDEX]

        return []

    def get_legal_actions(self) -> list[pacai.core.action.Action]:
        board = typing.cast(pacai.gridworld.board.Board, self.board)

        # If we are on a terminal position, we can only exit.
        position = self.get_agent_position()
        if ((position is not None) and board.is_terminal_position(position)):
            return [pacai.gridworld.mdp.ACTION_EXIT]

        return super().get_legal_actions()

    def sprite_lookup(self,
            sprite_sheet: pacai.core.spritesheet.SpriteSheet,
            position: pacai.core.board.Position,
            marker: pacai.core.board.Marker | None = None,
            action: pacai.core.action.Action | None = None,
            adjacency: pacai.core.board.AdjacencyString | None = None,
            animation_key: str | None = None,
            ) -> PIL.Image.Image:
        sprite = super().sprite_lookup(sprite_sheet, position, marker = marker, action = action, adjacency = adjacency, animation_key = animation_key)

        if (marker == pacai.gridworld.board.MARKER_DISPLAY_QVALUE):
            sprite = self._add_qvalue_info(sprite_sheet, sprite, position)

        return sprite

    def skip_draw(self,
            marker: pacai.core.board.Marker,
            position: pacai.core.board.Position,
            static: bool = False,
            ) -> bool:
        """ Return true if this marker/position combination should not be drawn on the board. """

        if (static):
            return False

        return position in self.board.get_marker_positions(pacai.gridworld.board.MARKER_DISPLAY_QVALUE)

    def get_static_positions(self) -> list[pacai.core.board.Position]:
        """ Get a list of positions to draw on the board statically. """

        return list(self.board.get_marker_positions(pacai.gridworld.board.MARKER_DISPLAY_QVALUE))

    def _add_qvalue_info(self,
            sprite_sheet: pacai.core.spritesheet.SpriteSheet,
            sprite: PIL.Image.Image,
            position: pacai.core.board.Position) -> PIL.Image.Image:
        """ Add the colored q-value triangles to the sprite. """

        board = typing.cast(pacai.gridworld.board.Board, self.board)

        sprite = sprite.copy()

        canvas = PIL.ImageDraw.Draw(sprite)

        # The offset from the visualization position to the true board position.
        # The Q-values are below the true board.
        base_offset = pacai.core.board.Position(-(board._original_height + 1), 0)
        base_position = position.add(base_offset)
        mdp_state = pacai.gridworld.mdp.GridWorldMDPState(base_position)

        for (i, point_offsets) in enumerate(QVALUE_TRIANGLE_POINT_OFFSETS):
            points = []

            for point_offset in point_offsets:
                # Offset the outer points of the triangle towards the inside of the triangle to avoid border overlaps.
                origin = [0, 0]
                for (i, offset) in enumerate(point_offset):
                    if (math.isclose(offset, 0.0)):
                        origin[i] = TRIANGLE_WIDTH
                    elif (math.isclose(offset, 1.0)):
                        origin[i] = -TRIANGLE_WIDTH

                point = (
                    (origin[0] + (sprite_sheet.width * point_offset[0])),
                    (origin[1] + (sprite_sheet.height * point_offset[1])),
                )
                points.append(tuple(point))

            qvalue = self._qvalues.get(mdp_state, {}).get(pacai.core.action.CARDINAL_DIRECTIONS[i], 0.0)
            color = self._red_green_gradient(qvalue, -1, 1)
            canvas.polygon(points, fill = color, outline = sprite_sheet.text, width = 1)

        return sprite

    def _red_green_gradient(self, value: float, min_value: float, max_value: float, blue: int = 75) -> tuple[int, int, int]:
        """ Get a color (RGB) between red (min) and green (max) based on the given value. """

        if (min_value >= max_value):
            raise ValueError(f"Gradient values are not in the correct order. Found: min = {min_value}, max = {max_value}.")

        value = min(max_value, max(min_value, value))
        ratio = (value - min_value) / (max_value - min_value)

        return (int(255 * (1.0 - ratio)), int(255 * ratio), blue)

    def process_turn(self,
            action: pacai.core.action.Action,
            rng: random.Random | None = None,
            mdp: pacai.gridworld.mdp.GridWorldMDP | None = None,
            **kwargs) -> None:
        if (rng is None):
            logging.warning("No RNG passed to pacai.gridworld.gamestate.GameState.process_turn().")
            rng = random.Random()

        if (mdp is None):
            raise ValueError("No MDP passed to pacai.gridworld.gamestate.GameState.process_turn().")

        board = typing.cast(pacai.gridworld.board.Board, self.board)

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
            board.remove_marker(pacai.gridworld.board.AGENT_MARKER, old_position)
            board.place_marker(pacai.gridworld.board.AGENT_MARKER, new_position)

        # Check if we are going to "win".
        # The reward for a terminal state is awarded on the action before EXIT.
        if (board.is_terminal_position(new_position) and (board.get_terminal_value(new_position) > 0)):
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

    def get_static_text(self) -> list[pacai.core.font.BoardText]:
        board = typing.cast(pacai.gridworld.board.Board, self.board)

        texts = []

        # Add on terminal values.
        for (position, value) in board._terminal_values.items():
            texts.append(pacai.core.font.BoardText(position, str(value), pacai.core.font.FontSize.SMALL))

        # If we are using the extended display, fill in all the information.
        if (board.display_qvalues()):
            texts += self._get_qdisplay_static_text()

        return texts

    def _get_qdisplay_static_text(self) -> list[pacai.core.font.BoardText]:
        board = typing.cast(pacai.gridworld.board.Board, self.board)

        # The offset from the visualization position to the true board position.
        # The Q-values are below the true board.
        base_offset = pacai.core.board.Position(-(board._original_height + 1), 0)

        texts = []

        # Add labels on the separator.
        row = (self.board.height - 1) // 2
        texts.append(pacai.core.font.BoardText(pacai.core.board.Position(row, 1), ' ↓ Q-Values'))
        texts.append(pacai.core.font.BoardText(pacai.core.board.Position(row, self.board.width - 2), '↑ Values'))

        for position in self.board.get_marker_positions(pacai.gridworld.board.MARKER_DISPLAY_QVALUE):
            # [(vertical alignment, horizontal alignment), ...]
            alignments = [
                (pacai.core.font.TextVerticalAlign.TOP, pacai.core.font.TextHorizontalAlign.CENTER),
                (pacai.core.font.TextVerticalAlign.MIDDLE, pacai.core.font.TextHorizontalAlign.RIGHT),
                (pacai.core.font.TextVerticalAlign.BOTTOM, pacai.core.font.TextHorizontalAlign.CENTER),
                (pacai.core.font.TextVerticalAlign.MIDDLE, pacai.core.font.TextHorizontalAlign.LEFT),
            ]

            base_position = position.add(base_offset)
            mdp_state = pacai.gridworld.mdp.GridWorldMDPState(base_position)

            for (i, alignment) in enumerate(alignments):
                action = pacai.core.action.CARDINAL_DIRECTIONS[i]
                qvalue = self._qvalues.get(mdp_state, {}).get(action, 0.0)

                vertical_align, horizontal_align = alignment
                texts.append(pacai.core.font.BoardText(
                        position, f"{qvalue:0.2f}",
                        size = pacai.core.font.FontSize.TINY,
                        vertical_align = vertical_align,
                        horizontal_align = horizontal_align,
                        color = (0, 0, 0)))

        return texts

    def to_dict(self) -> dict[str, typing.Any]:
        data = super().to_dict()
        data['_win'] = self._win
        return data

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        game_state = super().from_dict(data)
        game_state._win = data['_win']
        return game_state
