import pacai.core.agent
import pacai.test.base
import pacai.util.reflection

class TicketTest(pacai.test.base.BaseTest):
    def test_class_reference_base(self):
        # [(text, expected error substring, (filename, module_name, class_name)), ...]
        test_cases = [
            (
                'ClassReference',
                None,
                (None, None, 'ClassReference'),
            ),
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
                'pacai/util/reflection.py:pacai.util.reflection.ClassReference',
                None,
                ('pacai/util/reflection.py', 'pacai.util.reflection', 'ClassReference'),
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
