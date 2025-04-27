import glob
import os

import pacai.core.board
import pacai.test.base

class BoardTest(pacai.test.base.BaseTest):
    # Load all the known/included boards.
    def test_load_default_boards(self):
        for path in glob.glob(os.path.join(pacai.core.board.BOARDS_DIR, '*.board')):
            with self.subTest(msg = path):
                pacai.core.board.load_path(path)

    def test_load_test_boards(self):
        # [(board, expected error substring), ...]
        test_cases = [
            (TEST_BOARD_NO_SEP, None),
            (TEST_BOARD_OPTIONS, None),
            (TEST_BOARD_SEP_EMPTY_OPTIONS, None),
            (TEST_BOARD_AGENT, None),
            (TEST_BOARD_AGENTS, None),
            (TEST_BOARD_AGENTS_NUMBERS, None),

            ('', 'A board cannot be empty.'),
            (TEST_BOARD_ERROR_EMPTY_BOARD, 'A board cannot be empty.'),
            (TEST_BOARD_ERROR_FULL_EMPTY, 'A board cannot be empty.'),
            (TEST_BOARD_ERROR_FULL_EMPTY_SEP, 'A board cannot be empty.'),

            (TEST_BOARD_ERROR_BAD_CLASS, 'Cannot find class'),

            (TEST_BOARD_ERROR_WIDTH_ZERO, 'A board must have at least one column.'),
            (TEST_BOARD_ERROR_INCONSISTENT_WIDTH, 'Unexpected width'),

            (TEST_BOARD_ERROR_UNKNOWN_MARKER, 'Unknown marker'),

            (TEST_BOARD_ERROR_DUP_AGENTS, 'Duplicate agents'),
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
%%%
% %
%%%
'''

TEST_BOARD_OPTIONS = '''
{"class": "pacai.core.board.Board"}
---
%%%
% %
%%%
'''

TEST_BOARD_SEP_EMPTY_OPTIONS = '''
---
%%%
% %
%%%
'''

TEST_BOARD_AGENT = '''
%%%
%0%
%%%
'''

TEST_BOARD_AGENTS = '''
%%%%%
%0 1%
%%%%%
'''

TEST_BOARD_AGENTS_NUMBERS = '''
%%%%%
%9 3%
%%%%%
'''

TEST_BOARD_ERROR_DUP_AGENTS = '''
%%%%%
%0 0%
%%%%%
'''

TEST_BOARD_ERROR_EMPTY_BOARD = '''
{"class": "pacai.core.board.Board"}
---
'''

TEST_BOARD_ERROR_FULL_EMPTY = '''
'''

TEST_BOARD_ERROR_FULL_EMPTY_SEP = '''
---
'''

TEST_BOARD_ERROR_BAD_CLASS = '''
{"class": "pacai.core.board.ZZZ"}
---
%%%
% %
%%%
'''

TEST_BOARD_ERROR_WIDTH_ZERO = '''
{"strip": false}
---

'''

TEST_BOARD_ERROR_INCONSISTENT_WIDTH = '''
%%%
% %%
%%%%%
'''

TEST_BOARD_ERROR_UNKNOWN_MARKER = '''
%%%
%?%
%%%
'''
