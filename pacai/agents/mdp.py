import abc
import logging
import typing

import pacai.core.agent
import pacai.core.agentaction
import pacai.core.gamestate
import pacai.core.mdp

DEFAULT_LEARNING_RATE: float = 0.5
DEFAULT_DISCOUNT_RATE: float = 0.9
DEFAULT_EXPLORATION_RATE: float = 0.3

class MDPAgent(pacai.core.agent.Agent):
    """
    An agent that conceptually builds on top of a Markov Decision Process (MDP).
    The agent does not need an actual MDP, it may just model/approximate one.
    """

    def __init__(self,
            learning_rate: float = DEFAULT_LEARNING_RATE,
            discount_rate: float = DEFAULT_DISCOUNT_RATE,
            exploration_rate: float = DEFAULT_EXPLORATION_RATE,
            mdp_state_class: typing.Type | pacai.util.reflection.Reference | str | None = pacai.core.mdp.MDPStateBoard,
            **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        if (mdp_state_class is None):
            raise ValueError("ValueIterationAgent must be provided with an MDP state class.")

        clean_mdp_state_class = pacai.util.reflection.resolve_and_fetch(type, mdp_state_class)
        if (not issubclass(clean_mdp_state_class, pacai.core.mdp.MDPStatePosition)):
            name = pacai.util.reflection.get_qualified_name(clean_mdp_state_class)
            raise ValueError(f"Did not get a subclass of 'pacai.core.mdp.MDPStatePosition' for `mdp_state_class`, got '{name}'.")

        self.mdp_state_class: type[pacai.core.mdp.MDPStatePosition] = clean_mdp_state_class
        """ The function used to create MDP states from game states. """

        self.learning_rate: float = float(learning_rate)
        """
        The learning rate (alpha).

        May not be used by all MDP agents.
        """

        self.discount_rate: float = float(discount_rate)
        """
        The discount rate (gamma).
        A "discount" is a reduction to some score (usually a past or future score).
        1.0 is no discount, and 0.0 is a full discount.

        May not be used by all MDP agents.
        """

        self.exploration_rate: float = float(exploration_rate)
        """
        The exploration rate (epsilon).
        0.0 means that the agent will never explore, and always follow the computed policy.
        1.0 means that the agent will always explore, and never follow the computed policy.

        May not be used by all MDP agents.
        """

        logging.debug("Created an MDP agent with learning rate %0.2f, discount rate %0.2f, and exploration rate %0.2f.",
                self.learning_rate, self.discount_rate, self.exploration_rate)

    @abc.abstractmethod
    def get_mdp_state_value(self, mdp_state: pacai.core.mdp.MDPStatePosition, game_state: pacai.core.gamestate.GameState) -> float:
        """
        Get the value of the given MDP state.
        The provided game state will be what the MDP state was generated from.
        Unknown/unrecognized states should return 0.0.
        """

    @abc.abstractmethod
    def get_policy_action(self, mdp_state: pacai.core.mdp.MDPStatePosition, game_state: pacai.core.gamestate.GameState) -> pacai.core.action.Action:
        """
        Get the best action for this MDP state according to the current policy.
        If there are no legal action, return pacai.core.action.STOP.
        """

    @abc.abstractmethod
    def get_qvalue(self,
            mdp_state: pacai.core.mdp.MDPStatePosition,
            game_state: pacai.core.gamestate.GameState,
            action: pacai.core.action.Action,
            ) -> float:
        """
        Get the Q-value of the given MDP state and action pair.
        Pairs that have no known Q-value should return 0.0.
        """

    def game_start_full(self,
            agent_index: int,
            suggested_seed: int,
            initial_state: pacai.core.gamestate.GameState,
            ) -> pacai.core.agentaction.AgentAction:
        agent_action = super().game_start_full(agent_index, suggested_seed, initial_state)

        # Pass the mdp state values and Q-values back to the game
        # so they can be displayed in the UI.

        serial_mdp_state_values = []  # [(MDP state, MDP state value), ...]
        serial_policy = []  # [(MDP state, action), ...]
        serial_qvalues = []  # [(MDP state, action, qvalue), ...]

        for row in range(initial_state.board.height):
            for col in range(initial_state.board.width):
                position = pacai.core.board.Position(row, col)

                mdp_state = self.mdp_state_class(position = position, game_state = initial_state)
                raw_mdp_state = mdp_state.to_dict()

                mdp_state_value = self.get_mdp_state_value(mdp_state, initial_state)
                serial_mdp_state_values.append((raw_mdp_state, mdp_state_value))

                serial_policy.append((raw_mdp_state, self.get_policy_action(mdp_state, initial_state)))

                for action in pacai.core.action.CARDINAL_DIRECTIONS:
                    qvalue = self.get_qvalue(mdp_state, initial_state, action)
                    serial_qvalues.append((raw_mdp_state, action, qvalue))

        agent_action.other_info['mdp_state_values'] = serial_mdp_state_values
        agent_action.other_info['policy'] = serial_policy
        agent_action.other_info['qvalues'] = serial_qvalues

        return agent_action
