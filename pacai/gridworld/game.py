import argparse
import random

import pacai.core.agentinfo
import pacai.core.board
import pacai.core.game
import pacai.core.gamestate
import pacai.gridworld.gamestate
import pacai.gridworld.mdp

class Game(pacai.core.game.Game):
    """
    A game following the standard rules of GridWorld.
    """

    def get_initial_state(self,
            rng: random.Random,
            board: pacai.core.board.Board,
            agent_infos: dict[int, pacai.core.agentinfo.AgentInfo]) -> pacai.core.gamestate.GameState:
        return pacai.gridworld.gamestate.GameState(board = board, agent_infos = agent_infos)

    def process_args(self, args: argparse.Namespace) -> None:
        self.game_info.extra_info['noise'] = args.noise
        self.game_info.extra_info['living_reward'] = args.living_reward

    def _call_state_process_turn_full(self,
            state: pacai.core.gamestate.GameState,
            action: pacai.core.action.Action,
            rng: random.Random) -> None:
        mdp = pacai.gridworld.mdp.GridWorldMDP(
                noise = self.game_info.extra_info['noise'],
                living_reward = self.game_info.extra_info['living_reward'])
        mdp.game_start(state)

        state.process_turn_full(action, rng, mdp = mdp)
