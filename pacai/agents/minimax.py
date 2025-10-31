import logging
import math
import typing

import pacai.core.action
import pacai.core.agent
import pacai.core.gamestate
import pacai.util.parse

DEFAULT_PLY_COUNT: int = 2

class MinimaxLikeAgent(pacai.core.agent.Agent):
    """
    An agent that follow the general procedure of Minimax,
    but is abstracted to support things like alpha-beta pruning and expectimax.

    Currently, minimax_step_max(), minimax_step_min(), and minimax_step_expected_min() are all filled with dummy implementations.
    Child classes should implement those to get proper minimax functionality.
    """

    def __init__(self,
            ply_count: int = DEFAULT_PLY_COUNT,
            alphabeta_prune: bool = False,
            expectimax: bool = False,
            **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        # Parse (possibly string) arguments.
        ply_count = int(ply_count)
        alphabeta_prune = pacai.util.parse.boolean(alphabeta_prune)
        expectimax = pacai.util.parse.boolean(expectimax)

        if (ply_count < 1):
            raise ValueError(f"Ply count must be at least 1, found {ply_count}.")

        self.ply_count: int = ply_count
        """
        How many minimax plys to descend.
        A "ply" is one set of actions by each agent.
        When thinking about minimax in terms of a search tree,
        a ply will be a max layer followed by as many (usually min) layers until the original agent is reached again.
        """

        self.alphabeta_prune: bool = alphabeta_prune
        """ Whether or not to use alpha-beta pruning. """

        self.expectimax: bool = expectimax
        """ Whether or not to use expectimax. """

        self._stats_states_evaluated: list[int] = []
        """ Track how many states have been evaluated for each call to get_action(). """

        self._stats_nodes_visited: list[int] = []
        """ Track how many search nodes have been visited for each call to get_action(). """

    def evaluate_state(self,
            state: pacai.core.gamestate.GameState,
            action: pacai.core.action.Action | None = None,
            **kwargs: typing.Any) -> float:
        self._stats_states_evaluated[-1] += 1
        return super().evaluate_state(state, action)

    def game_complete(self, final_state: pacai.core.gamestate.GameState) -> None:
        logging.debug(("Minimax-like agent complete."
                + " Agent Index: %d, Ply Count: %d, Use Alpha-Beta Pruning: %s, Use Expectimax: %s,"
                + " States Evaluated: %d, Nodes Visited: %d."),
                self.agent_index,
                self.ply_count, self.alphabeta_prune, self.expectimax,
                sum(self._stats_states_evaluated), sum(self._stats_nodes_visited))

    def get_action(self, state: pacai.core.gamestate.GameState) -> pacai.core.action.Action:
        # Start the stat collection for this round at 0.
        self._stats_states_evaluated.append(0)
        self._stats_nodes_visited.append(0)

        actions, score = self.minimax_step(state, self.ply_count + 1, -math.inf, math.inf)
        action = self.rng.choice(actions)

        logging.debug("Turn: %d, Game State Score: %d, Minimax Score: %d, Chosen Action: %s, States Evaluated: %d, Nodes Visited: %d.",
                state.turn_count, state.score, score, action,
                self._stats_states_evaluated[-1], self._stats_nodes_visited[-1])

        if (action is None):
            raise ValueError("Did not get an action out of Minimax.")

        return action

    def minimax_step(self,
            state: pacai.core.gamestate.GameState,
            ply_count: int,
            alpha: float,
            beta: float,
            ) -> tuple[list[pacai.core.action.Action], float]:
        """
        Step through one layer (one agent) of minimax and return all the best actions (there may be ties) along with their score.
        This method will handle various book keeping and call the correct minimax_step_min() or minimax_step_max() method.

        When doing alpha-beta pruning,
        alpha represents the "best minimum" score
        while beta represents the "best maximum" score.
        They will typically start at inf and -inf, respectively.

        Return: ([best action, ...], best score).
        """

        self._stats_nodes_visited[-1] += 1

        # If we see ourselves, then we have descended a full ply.
        if (state.agent_index == self.agent_index):
            ply_count -= 1

        # At ply count zero, we just evaluate the current state and return up the tree.
        # Note that we only hit this when we are the target agent (since we just decremented the ply count).
        if (ply_count <= 0):
            return [], self.evaluate_state(state)

        # If the game is over, then stop descending.
        if (state.game_over):
            return [], self.evaluate_state(state)

        legal_actions = state.get_legal_actions()

        # Don't consider stopping unless we can do nothing else.
        # This will help keep the game moving along.
        if ((len(legal_actions) > 1) and (pacai.core.action.STOP in legal_actions)):
            legal_actions.remove(pacai.core.action.STOP)

        if (state.agent_index == self.agent_index):
            # We are considering ourselves, get the max.
            return self.minimax_step_max(state, ply_count, legal_actions, alpha, beta)

        # We are considering an opposing agent (like a ghost), get the min or expected min.
        if (self.expectimax):
            return [], self.minimax_step_expected_min(state, ply_count, legal_actions, alpha, beta)

        return self.minimax_step_min(state, ply_count, legal_actions, alpha, beta)

    def minimax_step_max(self,
            state: pacai.core.gamestate.GameState,
            ply_count: int,
            legal_actions: list[pacai.core.action.Action],
            alpha: float,
            beta: float,
            ) -> tuple[list[pacai.core.action.Action], float]:
        """
        Perform a max step in minimax.
        minimax_step() has already taken care of all the bookkeeping,
        this method just needs to return the best actions along with their score.

        alpha and beta can be ignored (and just passed along) when not doing alpha-beta pruning.

        The default implementation is just random and does not follow any minimax procedure.
        Child classes should override this method.

        Return: ([best action, ...], best score).
        """

        # Randomly choose an action.
        action = self.rng.choice(legal_actions)

        # Score the action.
        successor = state.generate_successor(action, self.rng)
        _, score = self.minimax_step(successor, ply_count, alpha, beta)

        return [action], score

    def minimax_step_min(self,
            state: pacai.core.gamestate.GameState,
            ply_count: int,
            legal_actions: list[pacai.core.action.Action],
            alpha: float,
            beta: float,
            ) -> tuple[list[pacai.core.action.Action], float]:
        """
        Perform a min step in minimax.
        minimax_step() has already taken care of all the bookkeeping,
        this method just needs to return the best actions along with their score.

        alpha and beta can be ignored (and just passed along) when not doing alpha-beta pruning.

        The default implementation is just random and does not follow any minimax procedure.
        Child classes should override this method.

        Return: ([best action, ...], best score).
        """

        # Randomly choose an action.
        action = self.rng.choice(legal_actions)

        # Score the action.
        successor = state.generate_successor(action, self.rng)
        _, score = self.minimax_step(successor, ply_count, alpha, beta)

        return [action], score

    def minimax_step_expected_min(self,
            state: pacai.core.gamestate.GameState,
            ply_count: int,
            legal_actions: list[pacai.core.action.Action],
            alpha: float,
            beta: float,
            ) -> float:
        """
        Perform a min step in expectimax.
        minimax_step() has already taken care of all the bookkeeping,
        this method just needs to return the expected score.

        Note that unlike minimax_step_max() and minimax_step_min(),
        no action is returned.

        alpha and beta can be ignored (and just passed along) when not doing alpha-beta pruning.

        The default implementation is just random and does not follow any minimax procedure.
        Child classes should override this method.
        """

        # Randomly choose an action.
        action = self.rng.choice(legal_actions)

        # Score the action.
        successor = state.generate_successor(action, self.rng)
        _, score = self.minimax_step(successor, ply_count, alpha, beta)

        return score
