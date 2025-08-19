import edq.testing.unittest
import edq.util.json

import pacai.core.agentaction
import pacai.core.agentinfo
import pacai.core.board_test
import pacai.core.game
import pacai.core.isolation.level
import pacai.core.ticket
import pacai.pacman.gamestate
import pacai.util.reflection

class JSONTest(edq.testing.unittest.BaseTest):
    """
    Test the JSON encoding/decoding functionality.
    """

    def test_dictconverter(self):
        """ Test subclasses of DictConverter. """

        # [(object, expected dict, expected error substring), ...]
        test_cases = [
            (
                pacai.util.reflection.Reference("a.b.c"),
                {
                    'short_name': 'c',
                    'module_name': 'a.b',
                    'file_path': None,
                },
                None,
            ),
            (
                pacai.util.reflection.Reference("test.py:c"),
                {
                    'short_name': 'c',
                    'module_name': None,
                    'file_path': 'test.py',
                },
                None,
            ),

            (
                pacai.core.agentinfo.AgentInfo(name = 'a.b'),
                {
                    'name': {
                        'short_name': 'b',
                        'module_name': 'a',
                        'file_path': None,
                    },
                    'move_delay': 100,
                    'state_eval_func': {
                        'short_name': 'base_eval',
                        'module_name': 'pacai.core.gamestate',
                        'file_path': None,
                    },
                    'extra_arguments': {},
                },
                None,
            ),
            (
                pacai.core.agentinfo.AgentInfo(name = 'a.b', foo = 'bar'),
                {
                    'name': {
                        'short_name': 'b',
                        'module_name': 'a',
                        'file_path': None,
                    },
                    'move_delay': 100,
                    'state_eval_func': {
                        'short_name': 'base_eval',
                        'module_name': 'pacai.core.gamestate',
                        'file_path': None,
                    },
                    'extra_arguments': {
                        'foo': 'bar',
                    },
                },
                None,
            ),

            (
                pacai.core.game.GameInfo(
                    'source',
                    {0: pacai.core.agentinfo.AgentInfo(name = 'a.b')},
                    seed = 4,
                ),
                {
                    "seed": 4,
                    "board_source": "source",
                    "agent_infos": {
                        0: {
                            "name": {
                                "file_path": None,
                                "module_name": "a",
                                "short_name": "b"
                            },
                            "move_delay": 100,
                            'state_eval_func': {
                                'short_name': 'base_eval',
                                'module_name': 'pacai.core.gamestate',
                                'file_path': None,
                            },
                            "extra_arguments": {}
                        }
                    },
                    "extra_info": {},
                    "isolation_level": "none",
                    "max_turns": -1,
                    "agent_start_timeout": 0.0,
                    "agent_end_timeout": 0.0,
                    "agent_action_timeout": 0.0,
                    "training": False,
                },
                None,
            ),
            (
                pacai.core.game.GameInfo(
                    'source',
                    {0: pacai.core.agentinfo.AgentInfo(name = 'a.b')},
                    seed = 4,
                    max_turns = 4,
                    agent_start_timeout = 1.0,
                    agent_end_timeout = 2.0,
                    agent_action_timeout = 3.0,
                    isolation_level = pacai.core.isolation.level.Level.PROCESS,
                    training = True,
                ),
                {
                    "seed": 4,
                    "board_source": "source",
                    "agent_infos": {
                        0: {
                            "name": {
                                "file_path": None,
                                "module_name": "a",
                                "short_name": "b"
                            },
                            "move_delay": 100,
                            'state_eval_func': {
                                'short_name': 'base_eval',
                                'module_name': 'pacai.core.gamestate',
                                'file_path': None,
                            },
                            "extra_arguments": {}
                        }
                    },
                    "extra_info": {},
                    "isolation_level": "process",
                    "max_turns": 4,
                    "agent_start_timeout": 1.0,
                    "agent_end_timeout": 2.0,
                    "agent_action_timeout": 3.0,
                    "training": True,
                },
                None,
            ),

            (
                pacai.core.board.Highlight(pacai.core.board.Position(row = 1, col = 2), 1),
                {
                    "position": {"row": 1, "col": 2},
                    "intensity": 1,
                },
                None,
            ),
            (
                pacai.core.board.Highlight(pacai.core.board.Position(row = 1, col = 2), 0.5),
                {
                    "position": {"row": 1, "col": 2},
                    "intensity": 500,
                },
                None,
            ),
            (
                pacai.core.board.Highlight(pacai.core.board.Position(row = 1, col = 2), None),
                {
                    "position": {"row": 1, "col": 2},
                    "intensity": None,
                },
                None,
            ),
            (
                pacai.core.board.Highlight(pacai.core.board.Position(row = 1, col = 2), 1),
                {
                    "position": {"row": 1, "col": 2},
                    "intensity": -1,
                },
                'Integer highlight intensity must be in',
            ),
            (
                pacai.core.board.Highlight(pacai.core.board.Position(row = 1, col = 2), 1),
                {
                    "position": {"row": 1, "col": 2},
                    "intensity": 10000000,
                },
                'Integer highlight intensity must be in',
            ),
            (
                pacai.core.board.Highlight(pacai.core.board.Position(row = 1, col = 2), 1),
                {
                    "position": {"row": 1, "col": 2},
                    "intensity": -0.1,
                },
                'Floating point highlight intensity must be in',
            ),
            (
                pacai.core.board.Highlight(pacai.core.board.Position(row = 1, col = 2), 1),
                {
                    "position": {"row": 1, "col": 2},
                    "intensity": 1.1,
                },
                'Floating point highlight intensity must be in',
            ),

            (
                pacai.core.agentaction.AgentAction(pacai.core.action.STOP),
                {
                    "action": "STOP",
                    "board_highlights": [],
                    "other_info": {},
                    "training_info": {},
                    "clear_inputs": False,
                },
                None,
            ),
            (
                pacai.core.agentaction.AgentAction(
                        action = pacai.core.action.STOP,
                        board_highlights = [
                             pacai.core.board.Highlight(pacai.core.board.Position(row = 1, col = 2), 0),
                             pacai.core.board.Highlight(pacai.core.board.Position(row = 3, col = 4), 1),
                        ],
                        other_info = {'foo': 'bar'},
                        training_info = {'weights': [0, 1, 2]},
                        clear_inputs = False,
                ),
                {
                    "action": "STOP",
                    "board_highlights": [
                        {
                            "position": {"row": 1, "col": 2},
                            "intensity": 0,
                        },
                        {
                            "position": {"row": 3, "col": 4},
                            "intensity": 1,
                        }
                    ],
                    "other_info": {
                        "foo": "bar",
                    },
                    "training_info": {'weights': [0, 1, 2]},
                    "clear_inputs": False,
                },
                None,
            ),

            (
                pacai.core.agentaction.AgentActionRecord(
                    agent_index = 0,
                    agent_action = pacai.core.agentaction.AgentAction(action = pacai.core.action.STOP),
                    duration = edq.util.time.Duration(10),
                    crashed = False,
                ),
                {
                    "agent_index": 0,
                    "agent_action": {
                        "action": "STOP",
                        "board_highlights": [],
                        "other_info": {},
                        "training_info": {},
                        "clear_inputs": False,
                    },
                    "duration": 10,
                    "crashed": False,
                    "timeout": False,
                },
                None,
            ),
            (
                pacai.core.agentaction.AgentActionRecord(
                    agent_index = 0,
                    agent_action = None,
                    duration = edq.util.time.Duration(10),
                    crashed = False,
                    timeout = True,
                ),
                {
                    "agent_index": 0,
                    "agent_action": None,
                    "duration": 10,
                    "crashed": False,
                    "timeout": True,
                },
                None,
            ),
            (
                pacai.core.agentaction.AgentActionRecord(
                    agent_index = 0,
                    agent_action = pacai.core.agentaction.AgentAction(
                        action = pacai.core.action.STOP,
                        board_highlights = [
                             pacai.core.board.Highlight(pacai.core.board.Position(row = 1, col = 2), 0),
                             pacai.core.board.Highlight(pacai.core.board.Position(row = 3, col = 4), 1),
                        ],
                        other_info = {'foo': 'bar'},
                        clear_inputs = True,
                    ),
                    duration = edq.util.time.Duration(10),
                    crashed = False,
                ),
                {
                    "agent_index": 0,
                    "agent_action": {
                        "action": "STOP",
                        "board_highlights": [
                            {
                                "position": {"row": 1, "col": 2},
                                "intensity": 0,
                            },
                            {
                                "position": {"row": 3, "col": 4},
                                "intensity": 1,
                            }
                        ],
                        "other_info": {
                            "foo": "bar",
                        },
                        "training_info": {},
                        "clear_inputs": True,
                    },
                    "duration": 10,
                    "crashed": False,
                    "timeout": False,
                },
                None,
            ),

            (
                pacai.core.game.GameResult(
                    1234,
                    pacai.core.game.GameInfo(
                        'source',
                        {0: pacai.core.agentinfo.AgentInfo(name = 'a.b')},
                        seed = 4,
                    ),
                    start_time = edq.util.time.Timestamp(12345),
                    agent_complete_records = {
                        0: pacai.core.agentaction.AgentActionRecord(
                            agent_index = 0,
                            agent_action = pacai.core.agentaction.AgentAction(
                                action = pacai.core.action.STOP,
                                other_info = {'value': 1},
                                training_info = {'value': 2},
                            ),
                            duration = edq.util.time.Duration(0),
                            crashed = False,
                        ),
                    },
                ),
                {
                    "game_id": 1234,
                    "game_info": {
                        "seed": 4,
                        "board_source": "source",
                        "agent_infos": {
                            0: {
                                "name": {
                                    "file_path": None,
                                    "module_name": "a",
                                    "short_name": "b"
                                },
                                "move_delay": 100,
                                'state_eval_func': {
                                    'short_name': 'base_eval',
                                    'module_name': 'pacai.core.gamestate',
                                    'file_path': None,
                                },
                                "extra_arguments": {}
                            }
                        },
                        "extra_info": {},
                        "isolation_level": "none",
                        "max_turns": -1,
                        "agent_start_timeout": 0.0,
                        "agent_end_timeout": 0.0,
                        "agent_action_timeout": 0.0,
                        "training": False,
                    },
                    "start_time": 12345,
                    "end_time": None,
                    "history": [],
                    "score": 0,
                    "game_timeout": False,
                    "timeout_agent_indexes": [],
                    "agent_complete_records": {
                        0: {
                            "agent_index": 0,
                            "agent_action": {
                                "action": "STOP",
                                "board_highlights": [],
                                "other_info": {'value': 1},
                                "training_info": {'value': 2},
                                "clear_inputs": False,
                            },
                            "duration": 0,
                            "crashed": False,
                            "timeout": False,
                        },
                    },
                    "crash_agent_indexes": [],
                    "winning_agent_indexes": [],
                },
                None,
            ),
            (
                pacai.core.game.GameResult(
                    1234,
                    pacai.core.game.GameInfo(
                        'source',
                        {0: pacai.core.agentinfo.AgentInfo(name = 'a.b')},
                        seed = 4,
                        max_turns = 4,
                        isolation_level = pacai.core.isolation.level.Level.PROCESS
                    ),
                    start_time = edq.util.time.Timestamp(12345),
                    history = [
                        pacai.core.agentaction.AgentActionRecord(
                            agent_index = 0,
                            agent_action = pacai.core.agentaction.AgentAction(action = pacai.core.action.STOP),
                            duration = edq.util.time.Duration(10),
                            crashed = False,
                        ),
                        pacai.core.agentaction.AgentActionRecord(
                            agent_index = 1,
                            agent_action = None,
                            duration = edq.util.time.Duration(20),
                            crashed = True,
                        ),
                    ],
                ),
                {
                    "game_id": 1234,
                    "game_info": {
                        "seed": 4,
                        "board_source": "source",
                        "agent_infos": {
                            0: {
                                "name": {
                                    "file_path": None,
                                    "module_name": "a",
                                    "short_name": "b"
                                },
                                "move_delay": 100,
                                'state_eval_func': {
                                    'short_name': 'base_eval',
                                    'module_name': 'pacai.core.gamestate',
                                    'file_path': None,
                                },
                                "extra_arguments": {}
                            }
                        },
                        "extra_info": {},
                        "isolation_level": "process",
                        "max_turns": 4,
                        "agent_start_timeout": 0.0,
                        "agent_end_timeout": 0.0,
                        "agent_action_timeout": 0.0,
                        "training": False,
                    },
                    "start_time": 12345,
                    "end_time": None,
                    "history": [
                        {
                            "agent_index": 0,
                            "agent_action": {
                                "action": "STOP",
                                "board_highlights": [],
                                "other_info": {},
                                "training_info": {},
                                "clear_inputs": False,
                            },
                            "duration": 10,
                            "crashed": False,
                            "timeout": False,
                        },
                        {
                            "agent_index": 1,
                            "agent_action": None,
                            "duration": 20,
                            "crashed": True,
                            "timeout": False,
                        },
                    ],
                    "score": 0,
                    "game_timeout": False,
                    "timeout_agent_indexes": [],
                    "agent_complete_records": {},
                    "crash_agent_indexes": [],
                    "winning_agent_indexes": [],
                },
                None,
            ),

            (
                pacai.core.ticket.Ticket(1, 2, 3),
                {
                    'next_time': 1,
                    'last_time': 2,
                    'num_moves': 3,
                },
                None,
            ),

            (
                pacai.core.ticket.Ticket(1, 2, 3),
                {
                    'next_time': 1,
                    'last_time': 2,
                    'num_moves': 3,
                },
                None,
            ),

            (
                pacai.core.board.Position(1, 2),
                {"row": 1, "col": 2},
                None
            ),

            (
                pacai.core.board.load_string('test', pacai.core.board_test.TEST_BOARD_AGENT),
                {
                    'source': 'test',
                    'markers': {
                        " ": " ",
                        "%": "%",
                        "0": "0",
                        "1": "1",
                        "2": "2",
                        "3": "3",
                        "4": "4",
                        "5": "5",
                        "6": "6",
                        "7": "7",
                        "8": "8",
                        "9": "9"
                    },
                    'height': 3,
                    'width': 3,
                    '_walls': [
                        {"row": 0, "col": 0},
                        {"row": 0, "col": 1},
                        {"row": 0, "col": 2},
                        {"row": 1, "col": 0},
                        {"row": 1, "col": 2},
                        {"row": 2, "col": 0},
                        {"row": 2, "col": 1},
                        {"row": 2, "col": 2},
                    ],
                    '_nonwall_objects': {
                        "0": [
                            {"row": 1, "col": 1},
                        ],
                    },
                    '_agent_initial_positions': {
                        "0": {"row": 1, "col": 1},
                    },
                    'search_target': None,
                },
                None,
            ),
            (
                pacai.core.board.load_string('test', pacai.core.board_test.TEST_BOARD_SEARCH_TARGET),
                {
                    'source': 'test',
                    'markers': {
                        " ": " ",
                        "%": "%",
                        "0": "0",
                        "1": "1",
                        "2": "2",
                        "3": "3",
                        "4": "4",
                        "5": "5",
                        "6": "6",
                        "7": "7",
                        "8": "8",
                        "9": "9"
                    },
                    'height': 3,
                    'width': 3,
                    '_walls': [
                        {"row": 0, "col": 0},
                        {"row": 0, "col": 1},
                        {"row": 0, "col": 2},
                        {"row": 1, "col": 0},
                        {"row": 1, "col": 2},
                        {"row": 2, "col": 0},
                        {"row": 2, "col": 1},
                        {"row": 2, "col": 2},
                    ],
                    '_nonwall_objects': {},
                    '_agent_initial_positions': {
                    },
                    'search_target': {
                        "row": 1,
                        "col": 2,
                    }
                },
                None,
            ),

            (
                pacai.pacman.gamestate.GameState(
                    seed = 4,
                    board = pacai.core.board.load_string('test', pacai.core.board_test.TEST_BOARD_AGENT),
                    agent_actions = {
                        0: [pacai.core.action.STOP],
                        1: [pacai.core.action.NORTH],
                    },
                    move_delays = {
                        0: 10,
                        1: 11,
                    },
                    tickets = {
                        0: pacai.core.ticket.Ticket(1, 2, 3),
                        1: pacai.core.ticket.Ticket(4, 5, 6),
                    }
                ),
                {
                    "seed": 4,
                    "board": {
                        'source': 'test',
                        'markers': {
                            " ": " ",
                            "%": "%",
                            "0": "0",
                            "1": "1",
                            "2": "2",
                            "3": "3",
                            "4": "4",
                            "5": "5",
                            "6": "6",
                            "7": "7",
                            "8": "8",
                            "9": "9"
                        },
                        'height': 3,
                        'width': 3,
                        '_walls': [
                            {"row": 0, "col": 0},
                            {"row": 0, "col": 1},
                            {"row": 0, "col": 2},
                            {"row": 1, "col": 0},
                            {"row": 1, "col": 2},
                            {"row": 2, "col": 0},
                            {"row": 2, "col": 1},
                            {"row": 2, "col": 2},
                        ],
                        '_nonwall_objects': {
                            "0": [
                                {"row": 1, "col": 1},
                            ],
                        },
                        '_agent_initial_positions': {
                            "0": {"row": 1, "col": 1},
                        },
                        "search_target": None,
                    },
                    'agent_actions': {
                        0: ["STOP"],
                        1: ["NORTH"],
                    },
                    "last_agent_index": -1,
                    'move_delays': {
                        0: 10,
                        1: 11,
                    },
                    'tickets': {
                        0: {
                            'next_time': 1,
                            'last_time': 2,
                            'num_moves': 3,
                        },
                        1: {
                            'next_time': 4,
                            'last_time': 5,
                            'num_moves': 6,
                        },
                    },
                    "agent_index": -1,
                    "game_over": False,
                    "score": 0,
                    "turn_count": 0,
                    "scared_timers": {},
                },
                None,
            ),

            (
                pacai.core.board.load_path('gridworld-book'),
                {
                    "_agent_initial_positions": {
                        "0": {"row": 3, "col": 1}
                    },
                    "_nonwall_objects": {
                        "0": [
                            {"row": 3, "col": 1},
                        ],
                        "T": [
                            {"row": 1, "col": 4},
                            {"row": 2, "col": 4},
                        ]
                    },
                    "_terminal_values": [
                        (
                            {"row": 1, "col": 4},
                            1
                        ),
                        (
                            {"row": 2, "col": 4},
                            -1
                        )
                    ],
                    "_walls": [
                        {"row": 0, "col": 0},
                        {"row": 0, "col": 1},
                        {"row": 0, "col": 2},
                        {"row": 0, "col": 3},
                        {"row": 0, "col": 4},
                        {"row": 0, "col": 5},
                        {"row": 1, "col": 0},
                        {"row": 1, "col": 5},
                        {"row": 2, "col": 0},
                        {"row": 2, "col": 2},
                        {"row": 2, "col": 5},
                        {"row": 3, "col": 0},
                        {"row": 3, "col": 5},
                        {"row": 4, "col": 0},
                        {"row": 4, "col": 1},
                        {"row": 4, "col": 2},
                        {"row": 4, "col": 3},
                        {"row": 4, "col": 4},
                        {"row": 4, "col": 5},
                    ],
                    "height": 5,
                    "markers": {
                        " ": " ",
                        "%": "%",
                        "0": "0",
                        "1": "1",
                        "2": "2",
                        "3": "3",
                        "4": "4",
                        "5": "5",
                        "6": "6",
                        "7": "7",
                        "8": "8",
                        "9": "9",
                        "T": "T"
                    },
                    "search_target": None,
                    "source": "gridworld-book",
                    "width": 6
                },
                None,
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            (original, expected_dict, error_substring) = test_case
            with self.subTest(msg = f"Case {i}:"):
                try:
                    actual_dict = original.to_dict()
                    obj_from_expected = original.from_dict(expected_dict)
                    obj_from_actual = original.from_dict(actual_dict)
                except Exception as ex:
                    if (error_substring is None):
                        self.fail(f"Unexpected error: '{str(ex)}'.")

                    self.assertIn(error_substring, str(ex), 'Error is not as expected.')
                    continue

                if (error_substring is not None):
                    self.fail(f"Did not get expected error: '{error_substring}'.")

                self.assertJSONDictEqual(expected_dict, actual_dict)

                self.assertJSONDictEqual(original, obj_from_expected)
                self.assertJSONDictEqual(original, obj_from_actual)
                self.assertJSONDictEqual(obj_from_expected, obj_from_actual)

    def test_loads_object(self):
        """ Test loading a JSON string into an object. """

        # [(text, class, expected error substring, expected object), ...]
        test_cases = [
            (
                """
                {
                    "name": {
                        "short_name": "b",
                        "module_name": "a",
                        "file_path": null,
                    }
                }
                """,
                pacai.core.agentinfo.AgentInfo,
                None,
                pacai.core.agentinfo.AgentInfo(name = 'a.b'),
            ),
            (
                """
                {
                    "name": {
                        "short_name": "b",
                        "module_name": "a",
                        "file_path": null,
                    },
                    "move_delay": 50
                }
                """,
                pacai.core.agentinfo.AgentInfo,
                None,
                pacai.core.agentinfo.AgentInfo(name = 'a.b', move_delay = 50),
            ),
            (
                """
                {
                    "name": {
                        "short_name": "b",
                        "module_name": "a",
                        "file_path": null,
                    },
                    "move_delay": 50,
                    "extra_arguments": {
                        "foo": "bar"
                    }
                }
                """,
                pacai.core.agentinfo.AgentInfo,
                None,
                pacai.core.agentinfo.AgentInfo(name = 'a.b', move_delay = 50, foo = 'bar'),
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            (text, cls, error_substring, expected) = test_case
            with self.subTest(msg = f"Case {i}:"):
                try:
                    actual = edq.util.json.loads_object(text, cls)
                except Exception as ex:
                    if (error_substring is None):
                        self.fail(f"Unexpected error: '{str(ex)}'.")

                    self.assertIn(error_substring, str(ex), 'Error is not as expected.')
                    continue

                if (error_substring is not None):
                    self.fail(f"Did not get expected error: '{error_substring}'.")

                self.assertJSONDictEqual(expected, actual)
