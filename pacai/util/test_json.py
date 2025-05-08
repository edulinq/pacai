import pacai.core.agentaction
import pacai.core.agentinfo
import pacai.core.game
import pacai.core.isolation.level
import pacai.core.test_board
import pacai.core.ticket
import pacai.pacman.gamestate
import pacai.test.base
import pacai.util.json
import pacai.util.reflection

class JSONTest(pacai.test.base.BaseTest):
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
                            "extra_arguments": {}
                        }
                    },
                    "isolation_level": "none",
                    "max_turns": -1
                },
                None,
            ),
            (
                pacai.core.game.GameInfo(
                    'source',
                    {0: pacai.core.agentinfo.AgentInfo(name = 'a.b')},
                    seed = 4,
                    max_turns = 4,
                    isolation_level = pacai.core.isolation.level.Level.PROCESS
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
                            "extra_arguments": {}
                        }
                    },
                    "isolation_level": "process",
                    "max_turns": 4
                },
                None,
            ),

            (
                pacai.core.board.Highlight(pacai.core.board.Position(row = 1, col = 2), 1),
                {
                    "position": {
                        "row": 1,
                        "col": 2,
                    },
                    "intensity": 1,
                },
                None,
            ),
            (
                pacai.core.board.Highlight(pacai.core.board.Position(row = 1, col = 2), 0.5),
                {
                    "position": {
                        "row": 1,
                        "col": 2,
                    },
                    "intensity": 500,
                },
                None,
            ),
            (
                pacai.core.board.Highlight(pacai.core.board.Position(row = 1, col = 2), None),
                {
                    "position": {
                        "row": 1,
                        "col": 2,
                    },
                    "intensity": None,
                },
                None,
            ),
            (
                pacai.core.board.Highlight(pacai.core.board.Position(row = 1, col = 2), 1),
                {
                    "position": {
                        "row": 1,
                        "col": 2,
                    },
                    "intensity": -1,
                },
                'Integer highlight intensity must be in',
            ),
            (
                pacai.core.board.Highlight(pacai.core.board.Position(row = 1, col = 2), 1),
                {
                    "position": {
                        "row": 1,
                        "col": 2,
                    },
                    "intensity": 10000000,
                },
                'Integer highlight intensity must be in',
            ),
            (
                pacai.core.board.Highlight(pacai.core.board.Position(row = 1, col = 2), 1),
                {
                    "position": {
                        "row": 1,
                        "col": 2,
                    },
                    "intensity": -0.1,
                },
                'Floating point highlight intensity must be in',
            ),
            (
                pacai.core.board.Highlight(pacai.core.board.Position(row = 1, col = 2), 1),
                {
                    "position": {
                        "row": 1,
                        "col": 2,
                    },
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
                ),
                {
                    "action": "STOP",
                    "board_highlights": [
                        {
                            "position": {
                                "row": 1,
                                "col": 2,
                            },
                            "intensity": 0,
                        },
                        {
                            "position": {
                                "row": 3,
                                "col": 4,
                            },
                            "intensity": 1,
                        }
                    ],
                    "other_info": {
                        "foo": "bar",
                    },
                },
                None,
            ),

            (
                pacai.core.agentaction.AgentActionRecord(
                    agent_index = 0,
                    agent_action = pacai.core.agentaction.AgentAction(action = pacai.core.action.STOP),
                    duration = pacai.util.time.Duration(10),
                    crashed = False,
                ),
                {
                    "agent_index": 0,
                    "agent_action": {
                        "action": "STOP",
                        "board_highlights": [],
                        "other_info": {},
                    },
                    "duration": 10,
                    "crashed": False,
                },
                None,
            ),
            (
                pacai.core.agentaction.AgentActionRecord(
                    agent_index = 0,
                    agent_action = None,
                    duration = pacai.util.time.Duration(10),
                    crashed = False,
                ),
                {
                    "agent_index": 0,
                    "agent_action": None,
                    "duration": 10,
                    "crashed": False,
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
                    ),
                    duration = pacai.util.time.Duration(10),
                    crashed = False,
                ),
                {
                    "agent_index": 0,
                    "agent_action": {
                        "action": "STOP",
                        "board_highlights": [
                            {
                                "position": {
                                    "row": 1,
                                    "col": 2,
                                },
                                "intensity": 0,
                            },
                            {
                                "position": {
                                    "row": 3,
                                    "col": 4,
                                },
                                "intensity": 1,
                            }
                        ],
                        "other_info": {
                            "foo": "bar",
                        },
                    },
                    "duration": 10,
                    "crashed": False,
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
                    start_time = pacai.util.time.Timestamp(12345),
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
                                "extra_arguments": {}
                            }
                        },
                        "isolation_level": "none",
                        "max_turns": -1,
                    },
                    "start_time": 12345,
                    "end_time": None,
                    "history": [],
                    "score": 0,
                    "game_timeout": False,
                    "timeout_agent_indexes": [],
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
                    start_time = pacai.util.time.Timestamp(12345),
                    history = [
                        pacai.core.agentaction.AgentActionRecord(
                            agent_index = 0,
                            agent_action = pacai.core.agentaction.AgentAction(action = pacai.core.action.STOP),
                            duration = pacai.util.time.Duration(10),
                            crashed = False,
                        ),
                        pacai.core.agentaction.AgentActionRecord(
                            agent_index = 1,
                            agent_action = None,
                            duration = pacai.util.time.Duration(20),
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
                                "extra_arguments": {}
                            }
                        },
                        "isolation_level": "process",
                        "max_turns": 4,
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
                            },
                            "duration": 10,
                            "crashed": False,
                        },
                        {
                            "agent_index": 1,
                            "agent_action": None,
                            "duration": 20,
                            "crashed": True,
                        },
                    ],
                    "score": 0,
                    "game_timeout": False,
                    "timeout_agent_indexes": [],
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
                {
                    "row": 1,
                    "col": 2,
                },
                None
            ),

            (
                pacai.core.board.load_string('test', pacai.core.test_board.TEST_BOARD_AGENT),
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
                    '_all_objects': {
                        "%": [
                            {"row": 0, "col": 0},
                            {"row": 0, "col": 1},
                            {"row": 0, "col": 2},
                            {"row": 1, "col": 0},
                            {"row": 1, "col": 2},
                            {"row": 2, "col": 0},
                            {"row": 2, "col": 1},
                            {"row": 2, "col": 2},
                        ],
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
                pacai.core.board.load_string('test', pacai.core.test_board.TEST_BOARD_SEARCH_TARGET),
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
                    '_all_objects': {
                        "%": [
                            {"row": 0, "col": 0},
                            {"row": 0, "col": 1},
                            {"row": 0, "col": 2},
                            {"row": 1, "col": 0},
                            {"row": 1, "col": 2},
                            {"row": 2, "col": 0},
                            {"row": 2, "col": 1},
                            {"row": 2, "col": 2},
                        ],
                    },
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
                    board = pacai.core.board.load_string('test', pacai.core.test_board.TEST_BOARD_AGENT),
                    last_actions = {
                        0: pacai.core.action.STOP,
                        1: pacai.core.action.NORTH,
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
                        '_all_objects': {
                            "%": [
                                {"row": 0, "col": 0},
                                {"row": 0, "col": 1},
                                {"row": 0, "col": 2},
                                {"row": 1, "col": 0},
                                {"row": 1, "col": 2},
                                {"row": 2, "col": 0},
                                {"row": 2, "col": 1},
                                {"row": 2, "col": 2},
                            ],
                            "0": [
                                {"row": 1, "col": 1},
                            ],
                        },
                        '_agent_initial_positions': {
                            "0": {"row": 1, "col": 1},
                        },
                        "search_target": None,
                    },
                    'last_actions': {
                        0: "STOP",
                        1: "NORTH",
                    },
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
                    "food_count": 0,
                    "scared_timers": {},
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

                self.assertDictEqualJSON(expected_dict, actual_dict)

                self.assertDictEqualJSON(original, obj_from_expected)
                self.assertDictEqualJSON(original, obj_from_actual)
                self.assertDictEqualJSON(obj_from_expected, obj_from_actual)

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
                    actual = pacai.util.json.loads_object(text, cls)
                except Exception as ex:
                    if (error_substring is None):
                        self.fail(f"Unexpected error: '{str(ex)}'.")

                    self.assertIn(error_substring, str(ex), 'Error is not as expected.')
                    continue

                if (error_substring is not None):
                    self.fail(f"Did not get expected error: '{error_substring}'.")

                self.assertDictEqualJSON(expected, actual)
