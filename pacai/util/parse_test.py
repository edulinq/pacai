import edq.testing.unittest

import pacai.util.parse

class ParseTest(edq.testing.unittest.BaseTest):
    """ Test parsing functionality. """

    def test_boolean(self):
        """ Test boolean parsing. """

        # [(text, expected, expected error substring), ...]
        test_cases = [
            ('true', True, None),
            ('True', True, None),
            ('TRUE', True, None),
            ('t', True, None),
            ('T', True, None),
            ('Yes', True, None),
            ('YES', True, None),
            ('yes', True, None),
            ('y', True, None),
            ('Y', True, None),
            ('1', True, None),

            (' true', True, None),
            ('true ', True, None),
            (' true ', True, None),

            (True, True, None),
            (1, True, None),

            ('false', False, None),
            ('False', False, None),
            ('FALSE', False, None),
            ('f', False, None),
            ('F', False, None),
            ('No', False, None),
            ('NO', False, None),
            ('no', False, None),
            ('n', False, None),
            ('N', False, None),
            ('0', False, None),

            (' false', False, None),
            ('false ', False, None),
            (' false ', False, None),

            (False, False, None),
            (0, False, None),

            ('a', None, 'Could not convert text to boolean'),
            (None, None, 'Could not convert text to boolean'),
            (5, None, 'Could not convert text to boolean'),
        ]

        for (i, test_case) in enumerate(test_cases):
            (text, expected, error_substring) = test_case
            with self.subTest(msg = f"Case {i} ('{text}'):"):
                try:
                    actual = pacai.util.parse.boolean(text)
                except Exception as ex:
                    if (error_substring is None):
                        self.fail(f"Unexpected error: '{str(ex)}'.")

                    self.assertIn(error_substring, str(ex), 'Error is not as expected.')
                    continue

                if (error_substring is not None):
                    self.fail(f"Did not get expected error: '{error_substring}'.")

                self.assertEqual(expected, actual)
