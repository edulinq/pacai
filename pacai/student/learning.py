import logging
import typing

import edq.util.json

import pacai.agents.mdp
import pacai.agents.userinput
import pacai.core.agent
import pacai.core.agentaction
import pacai.core.features
import pacai.core.gamestate
import pacai.core.mdp

DEFAULT_VALUE_ITERATIONS: int = 100

class ValueIterationAgent(pacai.agents.mdp.MDPAgent):
    """
    An agent that performs value iteration on an MDP to compute values for each MDP state.
    The agent then computes a policy based on those values and always follows the policy.
    """

    def __init__(self,
            mdp: pacai.core.mdp.MarkovDecisionProcess | None = None,
            iterations: int = DEFAULT_VALUE_ITERATIONS,
            **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        if (mdp is None):
            raise ValueError("ValueIterationAgent must be provided with an MDP.")

        self.mdp = mdp
        """ The MDP this agent will use. """

        self.mdp_state_values: dict[pacai.core.mdp.MDPStatePosition, float] = {}
        """ The value for each MDP state. """

        self.iterations: int = int(iterations)
        """ The number of value iterations to perform. """

    def game_start(self, initial_state: pacai.core.gamestate.GameState) -> None:
        # Initialize the MDP.
        self.mdp.game_start(initial_state)

        # Perform value iteration and set self.mdp_state_values.
        self.do_value_iteration(initial_state)

        super().game_start(initial_state)

    def do_value_iteration(self, game_state: pacai.core.gamestate.GameState) -> None:
        """
        Perform value iteration (for self.iteration) iterations
        and set self.mdp_state_values.
        """

        # *** Your Code Here ***

    def get_action(self, state: pacai.core.gamestate.GameState) -> pacai.core.action.Action:
        mdp_state = self.mdp_state_class(position = state.get_agent_position(), game_state = state)
        return self.get_policy_action(mdp_state, state)

    def get_mdp_state_value(self, mdp_state: pacai.core.mdp.MDPStatePosition, game_state: pacai.core.gamestate.GameState) -> float:
        return self.mdp_state_values.get(mdp_state, 0.0)

    def get_qvalue(self,
            mdp_state: pacai.core.mdp.MDPStatePosition,
            game_state: pacai.core.gamestate.GameState,
            action: pacai.core.action.Action,
            ) -> float:
        # *** Your Code Here ***
        return 0.0

    def get_policy_action(self, mdp_state: pacai.core.mdp.MDPStatePosition, game_state: pacai.core.gamestate.GameState) -> pacai.core.action.Action:
        # *** Your Code Here ***
        return pacai.core.action.STOP

class QLearningAgent(pacai.agents.mdp.MDPAgent):
    """
    An abstract value estimation agent that learns by estimating Q-values from experience.
    """

    def __init__(self,
            training_info: dict[str, typing.Any] | None = None,
            **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        self.last_state: pacai.core.gamestate.GameState | None = None
        """
        The last seen state.
        The difference between the last and current states will define the delta reward.
        """

        self.total_rewards: float = 0.0
        """
        The total rewards this agent as accumulated.
        Purely for display/logging purposes.
        """

        self.qvalues: dict[tuple[pacai.core.mdp.MDPStatePosition, pacai.core.action.Action], float] = {}
        """ The Q-values for this agent. """

        # Load any training information.
        if (training_info is not None):
            self.unpack_training_info(training_info)

    def pack_training_info(self) -> dict[str, typing.Any]:
        """
        Return a dict that contains all the training information to pass onto future iterations of this agent.
        This method will be used when this agent's epoch is complete to pass information to the next epoch's agent,
        which will use unpack_training_info() to load this data.
        The dict should be JSON serializable.
        """

        return {
            # [(raw mdp state, action, action), ...]
            'qvalues': [(mdp_state.to_dict(), action, qvalue) for ((mdp_state, action), qvalue) in self.qvalues.items()]
        }

    def unpack_training_info(self, data: dict[str, typing.Any]) -> None:
        """
        Load training information from the given dict,
        which should have been created by pack_training_info().
        """

        for (raw_mdp_state, raw_action, qvalue) in data.get('qvalues', []):
            mdp_state = self.mdp_state_class.from_dict(raw_mdp_state)
            action = pacai.core.action.Action(raw_action)
            self.qvalues[(mdp_state, action)] = qvalue

    def game_start(self, initial_state: pacai.core.gamestate.GameState) -> None:
        self.last_state = initial_state

    def game_complete_full(self,
            final_state: pacai.core.gamestate.GameState,
            ) -> pacai.core.agentaction.AgentAction:
        if (self.training):
            logging.debug("Completed training epoch %d.", self.training_epoch)

        self.update(final_state)

        average_reward = 0.0
        num_actions = len(final_state.get_agent_actions(self.agent_index))

        if (num_actions > 0):
            average_reward = self.total_rewards / num_actions

        logging.debug("Made %d moves for a total of %0.2f rewards (average: %0.2f).",
                num_actions, self.total_rewards, average_reward)

        # Store the training information for the next epoch's agent.
        agent_action = super().game_complete_full(final_state)
        agent_action.training_info['training_info'] = self.pack_training_info()
        return agent_action

    def update(self, new_state: pacai.core.gamestate.GameState) -> None:
        """
        Update the agent based on the difference between the old state and new state.
        """

        # Get the most recent action.
        last_action = new_state.get_last_agent_action(self.agent_index)
        if (last_action is None):
            # No action has been taken yet, don't update.
            return

        # Update the last seen state.
        old_state = self.last_state
        self.last_state = new_state.copy()

        if (old_state is None):
            # We don't have an old state to compare against yet.
            return

        # Compute and store the score delta.
        score_delta = new_state.score - old_state.score
        self.total_rewards += score_delta

        # Do not update if we are not training.
        if (not self.training):
            return

        old_position = old_state.get_agent_position()
        if (old_position is None):
            # The agent was not on the board the last turn. Did they respawn?
            return

        new_position = self.last_positions[-1]

        self.update_qvalue(score_delta, last_action,
            old_state, new_state,
            old_position, new_position)

    def get_action(self, state: pacai.core.gamestate.GameState) -> pacai.core.action.Action:
        # Update the agent by learning from the environment.
        # This code should not change and anways be the first thing done in this method.
        self.update(state)

        # *** Your Code Here ***
        return pacai.core.action.STOP

    def get_mdp_state_value(self, mdp_state: pacai.core.mdp.MDPStatePosition, game_state: pacai.core.gamestate.GameState) -> float:
        # *** Your Code Here ***
        return 0.0

    def get_policy_action(self, mdp_state: pacai.core.mdp.MDPStatePosition, game_state: pacai.core.gamestate.GameState) -> pacai.core.action.Action:
        # *** Your Code Here ***
        return pacai.core.action.STOP

    def get_qvalue(self,
            mdp_state: pacai.core.mdp.MDPStatePosition,
            game_state: pacai.core.gamestate.GameState,
            action: pacai.core.action.Action,
            ) -> float:
        return self.qvalues.get((mdp_state, action), 0.0)

    def update_qvalue(self,
            reward: float,
            action: pacai.core.action.Action,
            old_game_state: pacai.core.gamestate.GameState, new_game_state: pacai.core.gamestate.GameState,
            old_position: pacai.core.board.Position | None, new_position: pacai.core.board.Position | None,
            ) -> None:
        """
        Update the Q-value for the specified transition.
        This method will only be called when we are sure we want to update the Q-value
        (i.e., we are training and all the required information is available).
        """

        # *** Your Code Here ***

class QLearningUserInputAgent(QLearningAgent):
    """
    A Q-learning agent that learns from user actions.
    In practical terms, this is not a very useful agent (we learn Q-values, but don't do anything with them).
    However, this agent can be useful if you want to see how specific actions affect the learned Q-values.
    """

    def __init__(self, **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        kwargs['remember_last_action'] = False
        self._user_input_agent: pacai.core.agent.Agent = pacai.agents.userinput.UserInputAgent(**kwargs)
        """ Keep an agent that already knows how to work with user inputs. """

    def game_start_full(self,
            agent_index: int,
            suggested_seed: int,
            initial_state: pacai.core.gamestate.GameState,
            ) -> pacai.core.agentaction.AgentAction:
        self._user_input_agent.game_start_full(agent_index, suggested_seed, initial_state)
        return super().game_start_full(agent_index, suggested_seed, initial_state)

    def game_complete_full(self,
            final_state: pacai.core.gamestate.GameState,
            ) -> pacai.core.agentaction.AgentAction:
        self._user_input_agent.game_complete_full(final_state)
        return super().game_complete_full(final_state)

    def get_action_full(self,
            state: pacai.core.gamestate.GameState,
            user_inputs: list[pacai.core.action.Action],
            ) -> pacai.core.agentaction.AgentAction:
        # Get the action from the parent Q-learner.
        agent_action = super().get_action_full(state, user_inputs)

        # Just return if the action is an EXIT.
        if (agent_action.action == pacai.core.mdp.ACTION_EXIT):
            return agent_action

        # If we are not exiting, then just ignore the Q-learning action.
        return self._user_input_agent.get_action_full(state, user_inputs)

class ApproximateQLearningAgent(QLearningAgent):
    """
    A Q-learning agent that uses features and weights as Q-values instead of explicitly remembering each state.
    """

    def __init__(self,
            feature_extractor_func: pacai.core.features.FeatureExtractor | pacai.util.reflection.Reference | str =
                pacai.core.features.score_feature_extractor,
            **kwargs: typing.Any) -> None:
        self.weights: pacai.core.features.WeightDict = pacai.core.features.WeightDict()
        """ The feature weights learned by this agent. """

        clean_feature_extractor_func = pacai.util.reflection.resolve_and_fetch(pacai.core.features.FeatureExtractor, feature_extractor_func)
        self.feature_extractor_func: pacai.core.features.FeatureExtractor = clean_feature_extractor_func
        """ The feature extractor that will be used to get features from a state. """

        # Call super after ensuring that the weights exists so the training data can be unpacked into it.
        super().__init__(**kwargs)

    def pack_training_info(self) -> dict[str, typing.Any]:
        return {
            'weights': self.weights,
        }

    def unpack_training_info(self, data: dict[str, typing.Any]) -> None:
        self.weights = pacai.core.features.WeightDict(data.get('weights', {}))

    def game_complete(self, final_state: pacai.core.gamestate.GameState) -> None:
        super().game_complete(final_state)

        logging.debug("Weights: %s.", edq.util.json.dumps(self.weights))

    def get_qvalue(self,
            mdp_state: pacai.core.mdp.MDPStatePosition,
            game_state: pacai.core.gamestate.GameState,
            action: pacai.core.action.Action,
            ) -> float:
        """
        Instead of using pre-computed Q-values for each state,
        this should return $ weights ⋅ features $,
        where `⋅` is the dot product operator.
        """

        # *** Your Code Here ***
        return 0.0

    def update_qvalue(self,
            reward: float,
            action: pacai.core.action.Action,
            old_game_state: pacai.core.gamestate.GameState, new_game_state: pacai.core.gamestate.GameState,
            old_position: pacai.core.board.Position | None, new_position: pacai.core.board.Position | None,
            ) -> None:
        # *** Your Code Here ***
        pass
