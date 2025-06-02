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

def set_cli_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """
    Set GridWorld-specific CLI arguments.
    This is a sibling to init_from_args(), as the arguments set here can be interpreted there.
    """

    parser.add_argument('--agent', dest = 'agent', metavar = 'AGENT_TYPE',
            action = 'store', type = str, default = pacai.util.alias.AGENT_USER_INPUT.short,
            help = ('Select the agent type will be used (default: %(default)s).'
                    + f' Builtin agents: {pacai.util.alias.AGENT_SHORT_NAMES}.'))

    parser.add_argument('--noise', dest = 'noise',
            action = 'store', type = float, default = pacai.gridworld.mdp.DEFAULT_NOISE,
            help = 'How often agent actions result in unintended movement (default %(default)s).')

    parser.add_argument('--living-reward', dest = 'living_reward',
            action = 'store', type = float, default = pacai.gridworld.mdp.DEFAULT_LIVING_REWARD,
            help = 'The Reward for living for a time step (default %(default)s).')

    parser.add_argument('--qvalue-display', dest = 'qvalue_display',
            action = 'store_true', default = False,
            help = 'Display values, poilcies, and q-values (default %(default)s).')

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
