"""
The main executable for running a game of GridWorld.
"""

import argparse
import sys
import typing

import pacai.core.agentinfo
import pacai.gridworld.game
import pacai.gridworld.gamestate
import pacai.gridworld.mdp
import pacai.util.bin
import pacai.util.alias

DEFAULT_BOARD: str = 'gridworld-book'
DEFAULT_SPRITE_SHEET: str = 'gridworld'

DEFAULT_EPSILON: float = 0.3
DEFAULT_ITERATIONS: int = 10
DEFAULT_EPISODES: int = 1
DEFAULT_LEARNING_RATE: float = 0.5
DEFAULT_LIVING_REWARD: float = 0.0
DEFAULT_DISCOUNT_RATE: float = 0.9

def set_cli_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """
    Set GridWorld-specific CLI arguments.
    This is a sibling to init_from_args(), as the arguments set here can be interpreted there.
    """

    parser.add_argument('--agent', dest = 'agent', metavar = 'AGENT_TYPE',
            action = 'store', type = str, default = pacai.util.alias.AGENT_USER_INPUT.short,
            help = ('Select the agent type will be used (default: %(default)s).'
                    + f' Builtin agents: {pacai.util.alias.AGENT_SHORT_NAMES}.'))

    # TEST - Some of these may be agent args, not CLI args.

    parser.add_argument('--epsilon', dest = 'epsilon',
            action = 'store', type = float, default = DEFAULT_EPSILON,
            help = 'The chance of taking a random action in Q-learning (default %(default)s).')

    parser.add_argument('--iterations', dest = 'iterations',
            action = 'store', type = int, default = DEFAULT_ITERATIONS,
            help = 'The number of rounds of value iteration (default %(default)s).')

    parser.add_argument('--episodes', dest = 'episodes',
            action = 'store', type = int, default = DEFAULT_EPISODES,
            help = 'The number of epsiodes of the MDP to run (default %(default)s).')

    parser.add_argument('--learning-rate', dest = 'learning_rate',
            action = 'store', type = float, default = DEFAULT_LEARNING_RATE,
            help = 'The Learning rate (default %(default)s).')

    parser.add_argument('--noise', dest = 'noise',
            action = 'store', type = float, default = pacai.gridworld.mdp.DEFAULT_NOISE,
            help = 'How often actions result in unintended directions (default %(default)s).')

    parser.add_argument('--living-reward', dest = 'living_reward',
            action = 'store', type = float, default = DEFAULT_LIVING_REWARD,
            help = 'The Reward for living for a time step (default %(default)s).')

    parser.add_argument('--discount_rate', dest = 'discount_rate',
            action = 'store', type = float, default = DEFAULT_DISCOUNT_RATE,
            help = 'The discount rate on future (default %(default)s).')

    parser.add_argument('--qvalue-display', dest = 'qvalue_display',
            action = 'store_true', default = False,
            help = 'Display values, poilcies, and q-values (default %(default)s).')

    # TEST - Replace with logging/debug?
    parser.add_argument('--value-steps', dest = 'value_steps',
            action = 'store_true', default = False,
            help = 'Display each step of value iteration (default %(default)s).')

    return parser

def init_from_args(args: argparse.Namespace) -> tuple[dict[int, pacai.core.agentinfo.AgentInfo], list[int], dict[str, typing.Any]]:
    """
    Take in args from a parser that was passed to set_cli_args(),
    and initialize the proper components.
    """

    mdp = pacai.gridworld.mdp.GridWorldMDP(
            noise = args.noise,
            living_reward = args.living_reward)

    data = {
        'name': args.agent,
        'remember_last_action': False,
        'mdp': mdp,
        'mdp_state_class': pacai.util.alias.MDP_STATE_CLASS_GRIDWORLD.long,
        'discount_rate': args.discount_rate,
        'iterations': args.iterations,
    }

    base_agent_infos: dict[int, pacai.core.agentinfo.AgentInfo] = {
        pacai.gridworld.gamestate.AGENT_INDEX: pacai.core.agentinfo.AgentInfo(**data),
    }

    board_options = {
        'qvalue_display': args.qvalue_display,
    }

    return base_agent_infos, [], board_options

def get_additional_ui_options(args: argparse.Namespace) -> dict[str, typing.Any]:
    """ Get additional options for the UI. """

    return {
        'sprite_sheet_path': DEFAULT_SPRITE_SHEET,
    }

def main() -> int:
    """ Invoke a game of GridWorld. """

    return pacai.util.bin.run_main(
        description = "Play a game of GridWorld.",
        default_board = DEFAULT_BOARD,
        game_class = pacai.gridworld.game.Game,
        custom_set_cli_args = set_cli_args,
        get_additional_ui_options = get_additional_ui_options,
        custom_init_from_args = init_from_args,
        winning_agent_indexes = {pacai.gridworld.gamestate.AGENT_INDEX},
    )

if (__name__ == '__main__'):
    sys.exit(main())
