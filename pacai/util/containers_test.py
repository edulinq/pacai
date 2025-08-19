import edq.testing.unittest

import pacai.util.containers

class ContainersTest(edq.testing.unittest.BaseTest):
    """ Test the provided containers. """

    def test_push_pop(self):
        """ Test the containers push/pop ordering. """

        # [(container, input items, output items,  expected error substring), ...]
        test_cases = [
            (
                pacai.util.containers.Stack(),
                [1, 2, 3],
                [3, 2, 1],
                None,
            ),
            (
                pacai.util.containers.Stack(),
                ['a', 'b', 'c'],
                ['c', 'b', 'a'],
                None,
            ),

            (
                pacai.util.containers.Queue(),
                [1, 2, 3],
                [1, 2, 3],
                None,
            ),
            (
                pacai.util.containers.Queue(),
                ['a', 'b', 'c'],
                ['a', 'b', 'c'],
                None,
            ),

            (
                pacai.util.containers.PriorityQueueWithFunction(int),
                [1, 2, 3],
                [1, 2, 3],
                None,
            ),
            (
                pacai.util.containers.PriorityQueueWithFunction(int),
                [3, 2, 1],
                [1, 2, 3],
                None,
            ),
            (
                pacai.util.containers.PriorityQueueWithFunction(len),
                ['ccc', 'a', 'bb'],
                ['a', 'bb', 'ccc'],
                None,
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            (container, input_items, expected_output, error_substring) = test_case
            with self.subTest(msg = f"Case {i}:"):
                try:
                    for item in input_items:
                        container.push(item)

                    actual_output = []
                    while (not container.is_empty()):
                        actual_output.append(container.pop())
                except Exception as ex:
                    if (error_substring is None):
                        self.fail(f"Unexpected error: '{str(ex)}'.")

                    self.assertIn(error_substring, str(ex), 'Error is not as expected.')
                    continue

                if (error_substring is not None):
                    self.fail(f"Did not get expected error: '{error_substring}'.")

                self.assertJSONListEqual(expected_output, actual_output)
