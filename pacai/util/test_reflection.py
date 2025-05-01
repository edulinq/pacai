import os

import pacai.core.agent
import pacai.test.base
import pacai.util.reflection

THIS_DIR: str = os.path.join(os.path.dirname(os.path.realpath(__file__)))

class TicketTest(pacai.test.base.BaseTest):
    def test_class_reference_base(self):
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
                'Cannot specify a short name alone',
                None,
            ),
            (
                'pacai/util/reflection.py:pacai.util.reflection.Reference',
                'both a file path and module name',
                None,
            ),
        ]

        for i in range(len(test_cases)):
            (text, error_substring, expected_parts) = test_cases[i]
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
        # [(reference, expected error substring, args, kwargs, expected_count), ...]
        test_cases = [
            (
                'pacai.util.test_reflection.TestClass',
                None,
                [],
                {},
                0,
            ),
            (
                'pacai/util/test_reflection.py:TestClass',
                None,
                [],
                {},
                0,
            ),
            (
                'pacai.util.test_reflection.TestClass',
                None,
                [1],
                {},
                1,
            ),
            (
                'pacai.util.test_reflection.TestClass',
                None,
                [],
                {'count': 2},
                2,
            ),
            (
                'pacai.util.test_reflection.TestClass',
                None,
                [],
                {'other': 3},
                0,
            ),
            (
                'pacai.util.test_reflection.TestClass',
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
                'pacai.util.test_reflection.TestClass',
                'got multiple values for argument',
                [1],
                {'count': 2},
                None,
            ),
        ]

        for i in range(len(test_cases)):
            (reference, error_substring, args, kwargs, expected_count) = test_cases[i]
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

class TestClass:
    def __init__(self, count = 0, **kwargs):
        self.count = count
