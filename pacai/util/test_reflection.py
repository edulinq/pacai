import os

import pacai.core.agent
import pacai.test.base
import pacai.util.reflection

THIS_DIR: str = os.path.join(os.path.dirname(os.path.realpath(__file__)))

class TicketTest(pacai.test.base.BaseTest):
    def test_class_reference_base(self):
        # [(text, expected error substring, (filename, module_name, class_name)), ...]
        test_cases = [
            (
                'reflection.ClassReference',
                None,
                (None, 'reflection', 'ClassReference'),
            ),
            (
                'pacai.util.reflection.ClassReference',
                None,
                (None, 'pacai.util.reflection', 'ClassReference'),
            ),
            (
                'pacai/util/reflection.py:ClassReference',
                None,
                ('pacai/util/reflection.py', None, 'ClassReference'),
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
                'without a class name',
                None,
            ),
            (
                'test.py:',
                'without a class name',
                None,
            ),
            (
                'ClassReference',
                'Cannot specify a class name alone',
                None,
            ),
            (
                'pacai/util/reflection.py:pacai.util.reflection.ClassReference',
                'both a filepath and module name',
                None,
            ),
        ]

        for i in range(len(test_cases)):
            (text, error_substring, expected_parts) = test_cases[i]
            with self.subTest(msg = f"Case {i}:"):
                try:
                    class_ref = pacai.util.reflection.ClassReference(text)
                except Exception as ex:
                    if (error_substring is None):
                        self.fail(f"Unexpected error: '{str(ex)}'.")

                    self.assertIn(error_substring, str(ex), 'Error is not as expected.')
                    continue

                if (error_substring is not None):
                    self.fail(f"Did not get expected error: '{error_substring}'.")

                actual_parts = (class_ref.filepath, class_ref.module_name, class_ref.class_name)
                self.assertEqual(expected_parts, actual_parts)

    def test_new_object_base(self):
        # [(class_ref, expected error substring, args, kwargs, expected_count), ...]
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
                'reflection.ClassReference',
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
            (class_ref, error_substring, args, kwargs, expected_count) = test_cases[i]
            with self.subTest(msg = f"Case {i}:"):
                try:
                    actual = pacai.util.reflection.new_object(class_ref, *args, **kwargs)
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
