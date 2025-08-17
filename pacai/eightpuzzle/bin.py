"""
The main executable for running a game of 8 Puzzle.
"""

import argparse
import logging
import random
import sys

import pacai.core.log
import pacai.eightpuzzle.board
import pacai.eightpuzzle.problem
import pacai.search.common
import pacai.util.alias
import pacai.util.reflection

def run(args: argparse.Namespace) -> int:
    """ Run a single game of 8 Puzzle. """

    rng = random.Random(args.seed)
    logging.debug("Using seed %d.", args.seed)

    puzzle = pacai.eightpuzzle.board.from_rng(rng)
    print(f"Starting Puzzle:\n{puzzle}\n")

    solver = pacai.util.reflection.fetch(args.solver)
    problem = pacai.eightpuzzle.problem.EightPuzzleSearchProblem(puzzle)

    solution = solver(problem, pacai.search.common.null_heuristic, rng)
    print(f"Solver ({args.solver}) found a path of {len(solution.actions)} moves: {solution.actions}.\n")

    current_puzzle = puzzle
    for (i, action) in enumerate(solution.actions):
        if (args.interactive):
            input('Press return for the next step ...')

        current_puzzle = current_puzzle.apply_action(action)
        print(f"After {i + 1} moves:\n{current_puzzle}\n")

    print('Puzzle Solved!')

    return 0

def set_cli_args(parser: argparse.ArgumentParser) -> None:
    """
    Set specific CLI arguments.
    This is a sibling to init_from_args(), as the arguments set here can be interpreted there.
    """

    parser.add_argument('--seed', dest = 'seed',
            action = 'store', type = int, default = None,
            help = 'The random seed for the game (will be randomly generated if not set.')

    parser.add_argument('--interactive', dest = 'interactive',
            action = 'store_true', default = False,
            help = 'Wait until the user presses enter to show the next state (default: %(default)s).')

    parser.add_argument('--solver', dest = 'solver', metavar = 'SOLVER',
            action = 'store', type = str, default = pacai.util.alias.SEARCH_SOLVER_RANDOM.short,
            help = ('A reflection reference to the solver (pacai.core.search.SearchProblemSolver) to use (default: %(default)s).'
                    + ' Not all solvers can solve this problem.'
                    + f' Builtin solvers: {pacai.util.alias.SEARCH_SOLVER_SHORT_NAMES}.'))

def init_from_args(args: argparse.Namespace) -> argparse.Namespace:
    """
    Take in args from a parser that was passed to set_cli_args(),
    and initialize the proper components.
    """

    if (args.seed is None):
        args.seed = random.randint(0, 2**64)

    return args

def _parse_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    """ Parse the args from the parser returned by _get_parser(). """

    args = parser.parse_args()

    # Parse logging arguments.
    args = pacai.core.log.init_from_args(parser, args)

    # Parse specific options.
    args = init_from_args(args)

    return args

def _get_parser() -> argparse.ArgumentParser:
    """ Get a parser with all the options set to handle PacMan. """

    parser = argparse.ArgumentParser(description = "Play a game of 8 Puzzle.")

    # Add logging arguments.
    pacai.core.log.set_cli_args(parser)

    # Add specific options.
    set_cli_args(parser)

    return parser

def main() -> int:
    """ Invoke a game of 8 Puzzle. """

    args = _parse_args(_get_parser())
    return run(args)

if (__name__ == '__main__'):
    sys.exit(main())
