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

NON_SERIALIZED_FIELDS: list[str] = [
    '_mdp_state_values',
    '_minmax_mdp_state_values',
    '_policy',
    '_qvalues',
    '_minmax_qvalues',
]

class GameState(pacai.core.gamestate.GameState):
    """ A game state specific to a standard GridWorld game. """

    def __init__(self, **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        self._win: bool = False
        """ Keep track if the agent exited the game on a winning state. """

        self._mdp_state_values: dict[pacai.core.mdp.MDPStatePosition, float] = {}
        """
        The MDP state values computed by the agent.
        This member will not be serialized.
        """

        self._minmax_mdp_state_values: tuple[float, float] = (-1.0, 1.0)
        """
        The min and max MDP state values computed by the agent.
        This member will not be serialized.
        """

        self._policy: dict[pacai.core.mdp.MDPStatePosition, pacai.core.action.Action] = {}
        """
        The policy computed by the agent.
        This member will not be serialized.
        """

        self._qvalues: dict[pacai.core.mdp.MDPStatePosition, dict[pacai.core.action.Action, float]] = {}
        """
        The Q-values computed by the agent.
        This member will not be serialized.
        """

        self._minmax_qvalues: tuple[float, float] = (-1.0, 1.0)
        """
        The min and max Q-values computed by the agent.
        This member will not be serialized.
        """

    def agents_game_start(self, agent_responses: dict[int, pacai.core.agentaction.AgentActionRecord]) -> None:
        if (AGENT_INDEX not in agent_responses):
            return

        agent_action = agent_responses[AGENT_INDEX].agent_action
        if (agent_action is None):
            return

        if ('mdp_state_values' in agent_action.other_info):
            for (raw_mdp_state, value) in agent_action.other_info['mdp_state_values']:
                mdp_state = pacai.core.mdp.MDPStatePosition.from_dict(raw_mdp_state)
                self._mdp_state_values[mdp_state] = value

                min_value = min(self._mdp_state_values.values())
                max_value = max(self._mdp_state_values.values())
                self._minmax_mdp_state_values = (min_value, max_value)

        if ('policy' in agent_action.other_info):
            for (raw_mdp_state, raw_action) in agent_action.other_info['policy']:
                mdp_state = pacai.core.mdp.MDPStatePosition.from_dict(raw_mdp_state)
                action = pacai.core.action.Action(raw_action)
                self._policy[mdp_state] = action

        if ('qvalues' in agent_action.other_info):
            values = []

            for (raw_mdp_state, raw_action, qvalue) in agent_action.other_info['qvalues']:
                mdp_state = pacai.core.mdp.MDPStatePosition.from_dict(raw_mdp_state)
                action = pacai.core.action.Action(raw_action)

                if (mdp_state not in self._qvalues):
                    self._qvalues[mdp_state] = {}

                self._qvalues[mdp_state][action] = qvalue
                values.append(qvalue)

            self._minmax_qvalues = (min(values), max(values))

    def game_complete(self) -> list[int]:
        # If the agent exited on a positive terminal position, they win.
        if (self._win):
            return [AGENT_INDEX]

        return []

    def get_legal_actions(self, position: pacai.core.board.Position | None = None) -> list[pacai.core.action.Action]:
        board = typing.cast(pacai.gridworld.board.Board, self.board)

        if (position is None):
            position = self.get_agent_position()

        # If we are on a terminal position, we can only exit.
        if ((position is not None) and board.is_terminal_position(position)):
            return [pacai.core.mdp.ACTION_EXIT]

        # Otherwise, all cardinal directions (and STOP) are legal actions.
        return pacai.core.action.CARDINAL_DIRECTIONS + [pacai.core.action.STOP]

    def sprite_lookup(self,
            sprite_sheet: pacai.core.spritesheet.SpriteSheet,
            position: pacai.core.board.Position,
            marker: pacai.core.board.Marker | None = None,
            action: pacai.core.action.Action | None = None,
            adjacency: pacai.core.board.AdjacencyString | None = None,
            animation_key: str | None = None,
            ) -> PIL.Image.Image:
        board = typing.cast(pacai.gridworld.board.Board, self.board)

        sprite = super().sprite_lookup(sprite_sheet, position, marker = marker, action = action, adjacency = adjacency, animation_key = animation_key)

        if (marker == pacai.gridworld.board.MARKER_DISPLAY_VALUE):
            # Draw MDP state values and policies.
            sprite = self._add_mdp_state_value_sprite_info(sprite_sheet, sprite, position)
        elif (marker == pacai.gridworld.board.MARKER_DISPLAY_QVALUE):
            # Draw Q-values.
            sprite = self._add_qvalue_sprite_info(sprite_sheet, sprite, position)
        elif ((marker == pacai.gridworld.board.MARKER_TERMINAL)
                and ((position.row > board._original_height) or (position.col > board._original_width))):
            # Draw terminal values on the extended q-display.
            sprite = self._add_terminal_sprite_info(sprite_sheet, sprite, position)

        return sprite

    def skip_draw(self,
            marker: pacai.core.board.Marker,
            position: pacai.core.board.Position,
            static: bool = False,
            ) -> bool:
        if (static):
            return False

        board = typing.cast(pacai.gridworld.board.Board, self.board)
        return (position.row >= board._original_height) or (position.col >= board._original_width)

    def get_static_positions(self) -> list[pacai.core.board.Position]:
        board = typing.cast(pacai.gridworld.board.Board, self.board)

        positions = []
        for row in range(board.height):
            for col in range(board.width):
                if (row >= board._original_height) or (col >= board._original_width):
                    positions.append(pacai.core.board.Position(row, col))

        return positions

    def _add_terminal_sprite_info(self,
            sprite_sheet: pacai.core.spritesheet.SpriteSheet,
            sprite: PIL.Image.Image,
            position: pacai.core.board.Position) -> PIL.Image.Image:
        """ Add coloring to the terminal positions. """

        board = typing.cast(pacai.gridworld.board.Board, self.board)

        if (not board.is_terminal_position(position)):
            return sprite

        sprite = sprite.copy()
        canvas = PIL.ImageDraw.Draw(sprite)

        min_value = min(board._terminal_values.values())
        max_value = max(board._terminal_values.values())

        value = board.get_terminal_value(position)
        color = self._red_green_gradient(value, min_value, max_value)

        points = [(1, 1), (sprite_sheet.width - 1, sprite_sheet.height - 1)]
        canvas.rectangle(points, fill = color, outline = sprite_sheet.text, width = 1)

        return sprite

    def _add_mdp_state_value_sprite_info(self,
            sprite_sheet: pacai.core.spritesheet.SpriteSheet,
            sprite: PIL.Image.Image,
            position: pacai.core.board.Position) -> PIL.Image.Image:
        """ Add the colored q-value triangles to the sprite. """

        board = typing.cast(pacai.gridworld.board.Board, self.board)

        sprite = sprite.copy()
        canvas = PIL.ImageDraw.Draw(sprite)

        # The offset from the visualization position to the true board position.
        # The MDP state values are to the right of the true board.
        base_offset = pacai.core.board.Position(0, -(board._original_width + 1))
        base_position = position.add(base_offset)
        mdp_state = pacai.core.mdp.MDPStatePosition(position = base_position)

        value = self._mdp_state_values.get(mdp_state, 0.0)
        color = self._red_green_gradient(value, self._minmax_mdp_state_values[0], self._minmax_mdp_state_values[1])

        points = [(1, 1), (sprite_sheet.width - 1, sprite_sheet.height - 1)]
        canvas.rectangle(points, fill = color, outline = sprite_sheet.text, width = 1)

        return sprite

    def _add_qvalue_sprite_info(self,
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
        mdp_state = pacai.core.mdp.MDPStatePosition(position = base_position)

        for (direction_index, point_offsets) in enumerate(QVALUE_TRIANGLE_POINT_OFFSETS):
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

            qvalue = self._qvalues.get(mdp_state, {}).get(pacai.core.action.CARDINAL_DIRECTIONS[direction_index], 0.0)
            color = self._red_green_gradient(qvalue, self._minmax_qvalues[0], self._minmax_qvalues[1])
            canvas.polygon(points, fill = color, outline = sprite_sheet.text, width = 1)

        return sprite

    def _red_green_gradient(self, value: float,
            min_value: float, max_value: float, divider: float = 0.0,
            blue_intensity: float = 0.00) -> tuple[int, int, int]:
        """
        Get a color (RGB) between red (min) and green (max) based on the given value.
        Values under the divider will always be red, and values over will always be green.
        """

        if ((min_value > divider) or (divider > max_value)):
            raise ValueError(("Gradient values are not in the correct order."
                    + f"Found: min = {min_value}, divider = {divider}, max = {max_value}."))

        red_intensity = 0.0
        green_intensity = 0.0

        red_mass = max(0.01, divider - min_value)
        green_mass = max(0.01, max_value - divider)

        value = min(max_value, max(min_value, value))

        if (math.isclose(value, divider)):
            blue_intensity = 1.0
            red_intensity = 0.25
            green_intensity = 0.25
        elif (value < divider):
            red_intensity = 0.25 + (0.75 * (divider - value) / red_mass)
        else:
            green_intensity = 0.25 + (0.75 * (value - divider) / green_mass)

        return (int(255 * red_intensity), int(255 * green_intensity), int(255 * blue_intensity))

    def process_turn(self,
            action: pacai.core.action.Action,
            rng: random.Random | None = None,
            mdp: pacai.gridworld.mdp.GridWorldMDP | None = None,
            **kwargs: typing.Any) -> None:
        if (rng is None):
            logging.warning("No RNG passed to pacai.gridworld.gamestate.GameState.process_turn().")
            rng = random.Random(4)

        if (mdp is None):
            raise ValueError("No MDP passed to pacai.gridworld.gamestate.GameState.process_turn().")

        board = typing.cast(pacai.gridworld.board.Board, self.board)

        # Get the possible transitions from the MDP.
        transitions = mdp.get_transitions(mdp.get_starting_state(), action)

        # If there is only an exit transition, exit.
        if ((len(transitions) == 1) and (transitions[0].action == pacai.core.mdp.ACTION_EXIT)):
            logging.debug("Got the %s action, game is over.", pacai.core.mdp.ACTION_EXIT)
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
            text_color = None
            if ((position.row > board._original_height) or (position.col > board._original_width)):
                text_color = (0, 0, 0)

            texts.append(pacai.core.font.BoardText(position, str(value), size = pacai.core.font.FontSize.SMALL, color = text_color))

        # If we are using the extended display, fill in all the information.
        if (board.display_qvalues()):
            texts += self._get_qdisplay_static_text()

        return texts

    def _get_qdisplay_static_text(self) -> list[pacai.core.font.BoardText]:
        texts = []

        board = typing.cast(pacai.gridworld.board.Board, self.board)

        # Add labels on the separator.
        row = board._original_height
        texts.append(pacai.core.font.BoardText(pacai.core.board.Position(row, 1), ' ↓ Q-Values'))
        texts.append(pacai.core.font.BoardText(pacai.core.board.Position(row, board._original_width + 3), '  ↑ Values & Policy'))

        # Add text for MDP state values and policies.
        texts += self._get_qdisplay_static_text_mdp_state_values()

        # Add text for Q-values.
        texts += self._get_qdisplay_static_text_qvalues()

        return texts

    def _get_qdisplay_static_text_mdp_state_values(self) -> list[pacai.core.font.BoardText]:
        texts = []

        board = typing.cast(pacai.gridworld.board.Board, self.board)

        # The offset from the visualization position to the true board position.
        # The MDP state values are to the right of the true board.
        base_offset = pacai.core.board.Position(0, -(board._original_width + 1))

        for position in self.board.get_marker_positions(pacai.gridworld.board.MARKER_DISPLAY_VALUE):
            base_position = position.add(base_offset)
            mdp_state = pacai.core.mdp.MDPStatePosition(position = base_position)

            value = self._mdp_state_values.get(mdp_state, None)
            policy_action = self._policy.get(mdp_state, pacai.core.action.STOP)

            value_text = '?'
            if (value is not None):
                value_text = f"{value:0.2f}"

            policy_text = pacai.core.action.CARDINAL_DIRECTION_ARROWS.get(policy_action, '?')

            text = f"{value_text}\n{policy_text}"

            texts.append(pacai.core.font.BoardText(position, text,
                    size = pacai.core.font.FontSize.SMALL,
                    color = (0, 0, 0)))

        return texts

    def _get_qdisplay_static_text_qvalues(self) -> list[pacai.core.font.BoardText]:
        texts = []

        board = typing.cast(pacai.gridworld.board.Board, self.board)

        # The offset from the visualization position to the true board position.
        # The Q-values are below the true board.
        base_offset = pacai.core.board.Position(-(board._original_height + 1), 0)

        for position in self.board.get_marker_positions(pacai.gridworld.board.MARKER_DISPLAY_QVALUE):
            base_position = position.add(base_offset)
            mdp_state = pacai.core.mdp.MDPStatePosition(position = base_position)

            # [(vertical alignment, horizontal alignment), ...]
            alignments = [
                (pacai.core.font.TextVerticalAlign.TOP, pacai.core.font.TextHorizontalAlign.CENTER),
                (pacai.core.font.TextVerticalAlign.MIDDLE, pacai.core.font.TextHorizontalAlign.RIGHT),
                (pacai.core.font.TextVerticalAlign.BOTTOM, pacai.core.font.TextHorizontalAlign.CENTER),
                (pacai.core.font.TextVerticalAlign.MIDDLE, pacai.core.font.TextHorizontalAlign.LEFT),
            ]

            for (i, alignment) in enumerate(alignments):
                action = pacai.core.action.CARDINAL_DIRECTIONS[i]
                qvalue = self._qvalues.get(mdp_state, {}).get(action, None)

                text = '?'
                if (qvalue is not None):
                    text = f"{qvalue:0.2f}"

                vertical_align, horizontal_align = alignment
                texts.append(pacai.core.font.BoardText(
                        position, text,
                        size = pacai.core.font.FontSize.TINY,
                        vertical_align = vertical_align,
                        horizontal_align = horizontal_align,
                        color = (0, 0, 0)))

        return texts

    def to_dict(self) -> dict[str, typing.Any]:
        data = super().to_dict()
        data['_win'] = self._win

        for key in NON_SERIALIZED_FIELDS:
            if (key in data):
                del data[key]

        return data

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        game_state = super().from_dict(data)
        game_state._win = data['_win']
        return game_state
