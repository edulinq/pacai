"""
The main executable for running a game of GridWorld.
"""

import argparse
import sys

import pacai.core.agentinfo
import pacai.core.log
import pacai.core.ui
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

def run(args: argparse.Namespace) -> int:
    """ Run one or more gaames of GridWorld using pre-parsed arguments. """

    return pacai.util.bin.run_games(args, {pacai.gridworld.gamestate.AGENT_INDEX})

def set_cli_args(parser: argparse.ArgumentParser) -> None:
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

def init_from_args(args: argparse.Namespace) -> dict[int, pacai.core.agentinfo.AgentInfo]:
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
        'discount_rate': args.discount_rate,
        'iterations': args.iterations,
    }

    base_agent_infos: dict[int, pacai.core.agentinfo.AgentInfo] = {
        pacai.gridworld.gamestate.AGENT_INDEX: pacai.core.agentinfo.AgentInfo(**data),
    }

    return base_agent_infos

def _parse_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    """ Parse the args from the parser returned by _get_parser(). """

    args = parser.parse_args()

    # Parse logging arguments.
    args = pacai.core.log.init_from_args(args)

    # Parse ui arguments.
    additional_ui_args = {
        'sprite_sheet_path': DEFAULT_SPRITE_SHEET,
    }
    args = pacai.core.ui.init_from_args(args, additional_args = additional_ui_args)

    # Parse GridWorld-specific options.
    base_agent_infos = init_from_args(args)

    board_options = {
        'qvalue_display': args.qvalue_display,
    }

    # Parse game arguments.
    args = pacai.core.game.init_from_args(args, pacai.gridworld.game.Game,
            base_agent_infos = base_agent_infos,
            board_options = board_options)

    return args

def _get_parser() -> argparse.ArgumentParser:
    """ Get a parser with all the options set to handle GridWorld. """

    parser = argparse.ArgumentParser(description = "Play a game of GridWorld.")

    # Add logging arguments.
    pacai.core.log.set_cli_args(parser)

    # Add UI arguments.
    pacai.core.ui.set_cli_args(parser)

    # Add game arguments.
    pacai.core.game.set_cli_args(parser, default_board = DEFAULT_BOARD)

    # Add GridWorld-specific options.
    set_cli_args(parser)

    return parser

def main() -> int:
    """ Invoke a game of GridWorld. """

    args = _parse_args(_get_parser())
    return run(args)

if (__name__ == '__main__'):
    sys.exit(main())
