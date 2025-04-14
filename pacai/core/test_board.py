import glob
import os

import pacai.core.board
import pacai.test.base

class BoardTest(pacai.test.base.BaseTest):
    # Load all the known/included boards.
    def test_load_default_boards(self):
        for path in glob.glob(os.path.join(pacai.core.board.BOARDS_DIR, '*.txt')):
            pacai.core.board.load_path(path)

    def test_load_test_boards(self):
        # [(board, expected error substring), ...]
        test_cases = [
            ('', None),
            (TEST_BOARD_NO_SEP, None),
            (TEST_BOARD_OPTIONS, None),
            (TEST_BOARD_SEP_EMPTY_OPTIONS, None),
            (TEST_BOARD_EMPTY_BOARD, None),
            (TEST_BOARD_FULL_EMPTY, None),
            (TEST_BOARD_FULL_EMPTY_SEP, None),

            (TEST_BOARD_ERROR_BAD_CLASS, "Cannot find class 'ZZZ' in module 'pacai.core.board'."),
        ]

        for i in range(len(test_cases)):
            (text_board, error_substring) = test_cases[i]
            with self.subTest(msg = f"Case {i}:"):
                try:
                    pacai.core.board.load_string(text_board)
                except Exception as ex:
                    if (error_substring is None):
                        self.fail(f"Unexpected error: '{str(ex)}'.")

                    self.assertIn(error_substring, str(ex), 'Error is not as expected.')
                    continue

                if (error_substring is not None):
                    self.fail(f"Did not get expected error: '{error_substring}'.")

TEST_BOARD_NO_SEP = '''
%%%%%
%. P%
%%%%%
'''

TEST_BOARD_OPTIONS = '''
{"marker_wall": "#"}
---
#####
#. P#
#####
'''

TEST_BOARD_SEP_EMPTY_OPTIONS = '''
---
%%%%%
%. P%
%%%%%
'''

TEST_BOARD_EMPTY_BOARD = '''
{"marker_wall": "#"}
---
'''

TEST_BOARD_FULL_EMPTY = '''
'''

TEST_BOARD_FULL_EMPTY_SEP = '''
---
'''

TEST_BOARD_ERROR_BAD_CLASS = '''
{"class": "pacai.core.board.ZZZ"}
---
%%%%%
%. P%
%%%%%
'''
