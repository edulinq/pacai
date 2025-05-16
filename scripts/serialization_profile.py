#!/usr/bin/env python3

"""
This script is used as the source for profiling serialization of the core classes.
Specifically, the type of data what would be sent during TCP-level isolation.
Note that we are not trying to validate the output of the process,
just run it many times to profile it.
"""

import argparse
import os
import sys

THIS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)))
ROOT_DIR = os.path.join(THIS_DIR, '..')

sys.path.append(ROOT_DIR)

import pacai.core.board
import pacai.core.gamestate
import pacai.core.ticket
import pacai.util.alias
import pacai.util.json

def main(args):
    board = pacai.core.board.load_path('classic-medium')
    agent_infos = {
        0: pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_REFLEX),
        1: pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_RANDOM),
        2: pacai.core.agentinfo.AgentInfo(name = pacai.util.alias.AGENT_DUMMY),
    }

    state = pacai.core.gamestate.GameState(seed = 4, board = board, agent_infos = agent_infos)
    state.game_start()

    print('Starting serialization ...')

    for _ in range(args.count):
        json_data = state.to_dict()
        json_string = pacai.util.json.dumps(json_data)
        new_data = pacai.util.json.loads(json_string, strict = True)
        new_state = pacai.core.gamestate.GameState.from_dict(new_data)

    print(f"Completed {args.count} loops.")

def _load_args():
    parser = argparse.ArgumentParser(description = 'Perform many serializations for profiling.')

    parser.add_argument('--count', dest = 'count',
        action = 'store', type = int, default = 100,
        help = 'Loop this number of times (default: %(default)s).')

    return parser.parse_args()

if (__name__ == '__main__'):
    main(_load_args())
