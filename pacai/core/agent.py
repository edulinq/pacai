import abc
import logging
import random
import typing

import pacai.core.agentaction
import pacai.core.action
import pacai.core.agentinfo
import pacai.core.gamestate
import pacai.util.alias
import pacai.util.reflection

class Agent(abc.ABC):
    """
    The base for all agents in the pacai system.

    Agents are called on by the game engine for three things:
    1) `game_start_full()`/`game_start()` - a notification that the game has started.
    2) `game_complete()` - a notification that the game has ended.
    3) `get_action()` - a request for the agent to provide its next action.

    For the three core agent methods: get_action(), game_start(), and game_complete(),
    this class provides "full" versions of these methods (suffixed with "_full").
    These methods may have more information and allow the agent to provide more information,
    but are a little more complex.
    By default, this class will just call the simple methods from the "full" ones,
    allowing children to just implement the simple methods.

    Agents should avoid doing any heavy work in their constructors,
    and instead do that work in game_start_full()/game_start() (where they will have access to the game state).
    """

    def __init__(self,
            name: pacai.util.reflection.Reference | str = pacai.util.alias.AGENT_DUMMY.long,
            move_delay: int = pacai.core.agentinfo.DEFAULT_MOVE_DELAY,
            state_eval_func: pacai.core.gamestate.AgentStateEvaluationFunction | pacai.util.reflection.Reference | str =
                    pacai.core.agentinfo.DEFAULT_STATE_EVAL,
            training: bool = False,
            training_epoch: int = 0,
            **kwargs: typing.Any) -> None:
        self.name: pacai.util.reflection.Reference = pacai.util.reflection.Reference(name)
        """ The name of this agent. """

        self.move_delay: int = move_delay
        """
        The delay between moves for this agent.
        This value is abstract and has not real units,
        i.e., it is not something like a number of seconds.
        Instead, this is a relative "time" that is used to decide the next agent to move.
        Lower values (relative to other agents) times means the agent will move more times and thus be "faster".
        For example, an agent with a move delay of 50 will move twice as often as an agent with a move delay of 100.
        """

        clean_state_eval_func = pacai.util.reflection.resolve_and_fetch(pacai.core.gamestate.AgentStateEvaluationFunction, state_eval_func)
        self.evaluation_function: pacai.core.gamestate.AgentStateEvaluationFunction = clean_state_eval_func
        """ The evaluation function that agent will use to assess game states. """

        self.rng: random.Random = random.Random(4)
        """
        The RNG this agent should use whenever it wants randomness.
        This object will be constructed right away,
        but will be recreated with the suggested seed from the game engine during game_start_full().
        """

        self.agent_index: int = -1
        """
        The index this agent has been assigned for this game.
        It is initialized to -1 (before the game starts), but gets populated during game_start_full().
        """

        self.last_positions: list[pacai.core.board.Position | None] = []
        """
        Keep track of the last positions this agent was in.
        This is updated in the beginning of get_action_full().
        This will include times when the agent was not on the board (a None position).
        """

        self.training: bool = training
        """ This instance of this agent has been created for training. """

        self.training_epoch: int = training_epoch
        """ The training epoch (number of training games) the agent has completed. """

        self.extra_storage: dict[str, typing.Any] = {}
        """ An extra place that can be used by and agent subcomponents for persistent storage. """

        logging.debug("Created agent '%s' with move delay %d and state evaluation function '%s'.",
                pacai.util.reflection.get_qualified_name(self.name),
                self.move_delay,
                pacai.util.reflection.get_qualified_name(state_eval_func))

    def get_action_full(self,
            state: pacai.core.gamestate.GameState,
            user_inputs: list[pacai.core.action.Action],
            ) -> pacai.core.agentaction.AgentAction:
        """
        Get an action for this agent given the current state of the game.
        Agents may keep internal state, but the given state should be considered the source of truth.
        Calls to this method may be subject to a timeout (enforced by the isolator).

        By default, this method just calls get_action().
        Agent classes should typically just implement get_action(),
        and only implement this if they need additional functionality.
        """

        self.last_positions.append(state.get_agent_position(self.agent_index))

        action = self.get_action(state)

        return pacai.core.agentaction.AgentAction(action)

    def get_action(self, state: pacai.core.gamestate.GameState) -> pacai.core.action.Action:
        """
        Get an action for this agent given the current state of the game.
        This is simplified version of get_action_full(),
        see that method for full details.
        """

        return pacai.core.action.STOP

    def game_start_full(self,
            agent_index: int,
            suggested_seed: int,
            initial_state: pacai.core.gamestate.GameState,
            ) -> pacai.core.agentaction.AgentAction:
        """
        Notify this agent that the game is about to start.
        The provided agent index is the game's index/id for this agent.
        The state represents the initial state of the game.
        Any precomputation for this game should be done in this method.
        Calls to this method may be subject to a timeout.
        """

        self.agent_index = agent_index
        self.rng = random.Random(suggested_seed)

        self.game_start(initial_state)

        return pacai.core.agentaction.AgentAction(pacai.core.action.STOP)

    def game_start(self,
            initial_state: pacai.core.gamestate.GameState,
            ) -> None:
        """
        Notify this agent that the game is about to start.
        The provided agent index is the game's index/id for this agent.
        The state represents the initial state of the game.
        Any precomputation for this game should be done in this method.
        Calls to this method may be subject to a timeout.
        """

    def game_complete_full(self,
            final_state: pacai.core.gamestate.GameState,
            ) -> pacai.core.agentaction.AgentAction:
        """
        Notify this agent that the game has concluded.
        Agents should use this as an opportunity to make any final calculations and close any game-related resources.
        """

        self.game_complete(final_state)

        return pacai.core.agentaction.AgentAction(pacai.core.action.STOP)

    def game_complete(self,
            final_state: pacai.core.gamestate.GameState,
            ) -> None:
        """
        Notify this agent that the game has concluded.
        Agents should use this as an opportunity to make any final calculations and close any game-related resources.
        """

    def evaluate_state(self,
            state: pacai.core.gamestate.GameState,
            action: pacai.core.action.Action | None = None,
            **kwargs: typing.Any) -> float:
        """
        Evaluate the state to get a decide how good an action was.
        The base implementation for this function just calls `self.evaluation_function`,
        but child classes may override this method to easily implement their own evaluations.
        """

        return self.evaluation_function(state, agent = self, action = action, **kwargs)

def load(agent_info: pacai.core.agentinfo.AgentInfo) -> Agent:
    """
    Construct a new agent object using the given agent info.
    The name of the agent will be used as a reference to (e.g., name of) the agent's class.
    """

    agent = pacai.util.reflection.new_object(agent_info.name, **agent_info.to_flat_dict())

    if (not isinstance(agent, Agent)):
        raise ValueError(f"Loaded class is not an agent: '{agent_info.name}'.")

    return agent
