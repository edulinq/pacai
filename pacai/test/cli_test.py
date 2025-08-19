import os

import edq.testing.cli
import edq.testing.unittest

THIS_DIR: str = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
BASE_TESTDATA_DIR: str = os.path.join(THIS_DIR, "testdata", "cli")
TEST_CASES_DIR: str = os.path.join(BASE_TESTDATA_DIR, "tests")
DATA_DIR: str = os.path.join(BASE_TESTDATA_DIR, "data")

class CLITest(edq.testing.unittest.BaseTest):
    """ Test CLI invocations. """

# Populate CLITest with all the test methods.
edq.testing.cli.discover_test_cases(CLITest, TEST_CASES_DIR, DATA_DIR)
