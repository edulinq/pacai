import typing
import unittest

import edq.util.json

FORMAT_STR = "\n--- Expected ---\n%s\n--- Actual ---\n%s\n---\n"

class BaseTest(unittest.TestCase):
    """ A base test class to add common testing functionality. """

    maxDiff = None

    def assertDictEqualJSON(self, a: typing.Any, b: typing.Any) -> None:  # pylint: disable=invalid-name
        """
        Like unittest.TestCase.assertDictEqual(),
        but calls vars() on each object if they are not already dicts
        and uses JSON from the error message.
        """

        a_json = edq.util.json.dumps(a, indent = 4)
        b_json = edq.util.json.dumps(b, indent = 4)

        if (not isinstance(a, dict)):
            if (isinstance(a, edq.util.json.DictConverter)):
                a = a.to_dict()
            else:
                a = vars(a)

        if (not isinstance(b, dict)):
            if (isinstance(b, edq.util.json.DictConverter)):
                b = b.to_dict()
            else:
                b = vars(b)

        super().assertDictEqual(a, b, FORMAT_STR % (a_json, b_json))

    def assertListEqualJSON(self, a: list[typing.Any], b: list[typing.Any]) -> None:  # pylint: disable=invalid-name
        """ Like unittest.TestCase.assertLiseEqual(), but uses JSON formatting in the output. """

        a_json = edq.util.json.dumps(a, indent = 4)
        b_json = edq.util.json.dumps(b, indent = 4)

        super().assertListEqual(a, b, FORMAT_STR % (a_json, b_json))
