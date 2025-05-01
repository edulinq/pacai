import pacai.core.agentinfo
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
        ]

        for i in range(len(test_cases)):
            (original, expected_dict, error_substring) = test_cases[i]
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

        for i in range(len(test_cases)):
            (text, cls, error_substring, expected) = test_cases[i]
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
