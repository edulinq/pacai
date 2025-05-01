import pacai.util.json
import typing
import unittest

FORMAT_STR = "\n--- Expected ---\n%s\n--- Actual ---\n%s\n---\n"

class BaseTest(unittest.TestCase):
    """ A base test class to add common testing functionality. """

    maxDiff = None

    def assertDictEqualJSON(self, a: typing.Any, b: typing.Any) -> None:
        """
        Like unittest.TestCase.assertForcecdDictEqual(),
        but calls vars() on each object if they are not already dicts
        and uses JSON from the error message.
        """

        a_json = pacai.util.json.dumps(a, indent = 4)
        b_json = pacai.util.json.dumps(b, indent = 4)

        if (not isinstance(a, dict)):
            if (isinstance(a, pacai.util.json.DictConverter)):
                a = a.to_dict()
            else:
                a = vars(a)

        if (not isinstance(b, dict)):
            if (isinstance(b, pacai.util.json.DictConverter)):
                b = b.to_dict()
            else:
                b = vars(b)

        super().assertDictEqual(a, b, FORMAT_STR % (a_json, b_json))

    def assertListEqualJSON(self, a: list, b: list) -> None:
        a_json = pacai.util.json.dumps(a, indent = 4)
        b_json = pacai.util.json.dumps(b, indent = 4)

        super().assertListEqual(a, b, FORMAT_STR % (a_json, b_json))
