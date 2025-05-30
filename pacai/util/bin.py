import argparse
import logging
import typing

import pacai.core.agentaction
import pacai.core.game

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

    training_infos: dict[int, dict[str, typing.Any]] = {}
    training_results = []

    # Run training games/epochs.
    for i in range(args.num_training):
        game = args._games[i]

        for (agent_index, agent_info) in game.game_info.agent_infos.items():
            # Set information gained from the previous training epochs.
            data = training_infos.get(agent_index, {}).copy()

            # Tell agents we are training.
            data['training'] = True
            data['training_epoch'] = i

            agent_info.extra_arguments.update(data)

        result = game.run(args._ui)
        training_results.append(result)

        for (agent_index, agent_record) in result.agent_complete_records.items():
            if (agent_record.agent_action is not None):
                training_infos[agent_index] = agent_record.agent_action.training_info

    results = []

    for i in range(args.num_games):
        game = args._games[i + args.num_training]

        # Set any information gained from training.
        for (agent_index, training_info) in training_infos.items():
            game.game_info.agent_infos[agent_index].extra_arguments.update(training_info)

        result = game.run(args._ui)
        results.append(result)

    if (len(training_results) > 0):
        log_scores(training_results, winning_agent_indexes, prefix = 'Training ')

    if (len(results) > 0):
        log_scores(results, winning_agent_indexes)

    return 0

def log_scores(results: list[pacai.core.game.GameResult], winning_agent_indexes: set[int], prefix = '') -> None:
    """
    Log the result of running several games.
    """

    scores = [result.score for result in results]
    wins = [(not winning_agent_indexes.isdisjoint(set(result.winning_agent_indexes))) for result in results]
    win_rate = wins.count(True) / float(len(wins))
    turn_counts = [len(result.history) for result in results]

    logging.info('%sAverage Score: %s', prefix, sum(scores) / float(len(scores)))
    logging.info('%sScores:        %s', prefix, ', '.join([str(score) for score in scores]))
    logging.info('%sWin Rate:      %d / %d (%0.2f)', prefix, wins.count(True), len(wins), win_rate)
    logging.info('%sRecord:        %s', prefix, ', '.join([['Loss', 'Win'][int(win)] for win in wins]))
    logging.info('%sAverage Turns: %s', prefix, sum(turn_counts) / float(len(turn_counts)))
    logging.info('%sTurn Counts:   %s', prefix, ', '.join([str(turn_count) for turn_count in turn_counts]))
