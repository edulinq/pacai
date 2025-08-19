import sys

import edq.testing.unittest

import pacai.util.alias
import pacai.util.reflection

class AliasTest(edq.testing.unittest.BaseTest):
    """ Test alias functionality. """

    def test_alias_reflection(self):
        """ Test that all aliases marked as qualified names can be imported. """

        for (i, alias) in enumerate(pacai.util.alias.Alias._all_aliases):
            if (not alias.is_qualified_name):
                continue

            if (alias.skip_windows_test and sys.platform.startswith("win")):
                continue

            with self.subTest(msg = f"Case {i} ('{alias.long}'):"):
                pacai.util.reflection.fetch(alias.long)
