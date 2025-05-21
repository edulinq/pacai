import argparse
import logging

def run_games(
        args: argparse.Namespace,
        winning_agent_indexes: set[int] | None = None,
        ) -> int:
    """
    Run one or more standard games using pre-parsed arguments.
    The arguments are expected to have `_games` and `_ui`,
    as if `pacai.core.ui.init_from_args()` and `pacai.core.game.init_from_args()` have been called.
    """

    if (winning_agent_indexes is None):
        winning_agent_indexes = set()

    results = []
    for game in args._games:
        results.append(game.run(args._ui))

    scores = [result.score for result in results]
    wins = [(not winning_agent_indexes.isdisjoint(set(result.winning_agent_indexes))) for result in results]
    win_rate = wins.count(True) / float(len(wins))
    turn_counts = [len(result.history) for result in results]

    logging.info('Average Score: %s', sum(scores) / float(len(scores)))
    logging.info('Scores:        %s', ', '.join([str(score) for score in scores]))
    logging.info('Win Rate:      %d / %d (%0.2f)', wins.count(True), len(wins), win_rate)
    logging.info('Record:        %s', ', '.join([['Loss', 'Win'][int(win)] for win in wins]))
    logging.info('Average Turns: %s', sum(turn_counts) / float(len(turn_counts)))
    logging.info('Turn Counts:   %s', ', '.join([str(turn_count) for turn_count in turn_counts]))

    return 0
