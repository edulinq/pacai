import os

import edq.testing.unittest

import pacai.core.agent
import pacai.util.reflection

THIS_DIR: str = os.path.join(os.path.dirname(os.path.realpath(__file__)))

class ReflectionTest(edq.testing.unittest.BaseTest):
    """ Test reflection functionality. """

    def test_class_reference_base(self):
        """ Test creating (not instantiating) reflection referneces. """

        # [(text, expected error substring, (filename, module_name, short_name)), ...]
        test_cases = [
            (
                'reflection.Reference',
                None,
                (None, 'reflection', 'Reference'),
            ),
            (
                'pacai.util.reflection.Reference',
                None,
                (None, 'pacai.util.reflection', 'Reference'),
            ),
            (
                'pacai/util/reflection.py:Reference',
                None,
                ('pacai/util/reflection.py', None, 'Reference'),
            ),
            (
                pacai.util.reflection.Reference('pacai.util.reflection.Reference'),
                None,
                (None, 'pacai.util.reflection', 'Reference'),
            ),

            (
                'agent-dummy',
                None,
                (None, 'pacai.agents.dummy', 'DummyAgent'),
            ),

            # Special Paths

            (
                '/pacai/util/reflection.py:Reference',
                None,
                ('/pacai/util/reflection.py', None, 'Reference'),
            ),
            (
                r'pacai\util\reflection.py:Reference',
                None,
                (r'pacai\util\reflection.py', None, 'Reference'),
            ),
            (
                r'C:\pacai\util\reflection.py:Reference',
                None,
                (r'C:\pacai\util\reflection.py', None, 'Reference'),
            ),

            # Errors

            (
                '',
                'empty string',
                None,
            ),
            (
                '   ',
                'empty string',
                None,
            ),
            (
                ':',
                'without a short name',
                None,
            ),
            (
                'test.py:',
                'without a short name',
                None,
            ),
            (
                'Reference',
                'Cannot specify a (non-alias) short name alone',
                None,
            ),
            (
                'pacai/util/reflection.py:pacai.util.reflection.Reference',
                'both a file path and module name',
                None,
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            (text, error_substring, expected_parts) = test_case
            with self.subTest(msg = f"Case {i}:"):
                try:
                    reference = pacai.util.reflection.Reference(text)
                except Exception as ex:
                    if (error_substring is None):
                        self.fail(f"Unexpected error: '{str(ex)}'.")

                    self.assertIn(error_substring, str(ex), 'Error is not as expected.')
                    continue

                if (error_substring is not None):
                    self.fail(f"Did not get expected error: '{error_substring}'.")

                actual_parts = (reference.file_path, reference.module_name, reference.short_name)
                self.assertEqual(expected_parts, actual_parts)

    def test_new_object_base(self):
        """ Test creating new objects from reflection references. """

        # [(reference, expected error substring, args, kwargs, expected_count), ...]
        test_cases = [
            (
                'pacai.util.reflection_test._TestClass',
                None,
                [],
                {},
                0,
            ),
            (
                'pacai/util/reflection_test.py:_TestClass',
                None,
                [],
                {},
                0,
            ),
            (
                'pacai.util.reflection_test._TestClass',
                None,
                [1],
                {},
                1,
            ),
            (
                'pacai.util.reflection_test._TestClass',
                None,
                [],
                {'count': 2},
                2,
            ),
            (
                'pacai.util.reflection_test._TestClass',
                None,
                [],
                {'other': 3},
                0,
            ),
            (
                'pacai.util.reflection_test._TestClass',
                None,
                [4],
                {'other': 5},
                4,
            ),

            # Errors

            (
                'reflection.Reference',
                "Unable to locate module 'reflection'",
                [],
                {},
                None,
            ),
            (
                'pacai.util.reflection_test._TestClass',
                'got multiple values for argument',
                [1],
                {'count': 2},
                None,
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            (reference, error_substring, args, kwargs, expected_count) = test_case
            with self.subTest(msg = f"Case {i}:"):
                try:
                    actual = pacai.util.reflection.new_object(reference, *args, **kwargs)
                except Exception as ex:
                    if (error_substring is None):
                        self.fail(f"Unexpected error: '{str(ex)}'.")

                    self.assertIn(error_substring, str(ex), 'Error is not as expected.')
                    continue

                if (error_substring is not None):
                    self.fail(f"Did not get expected error: '{error_substring}'.")

                self.assertEqual(expected_count, actual.count)

class _TestClass:
    """ A class just for testing. """
    def __init__(self, count = 0, **kwargs):
        self.count = count
