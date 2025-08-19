import edq.testing.unittest

import pacai.core.board
import pacai.search.distance
import pacai.search.position

class DistanceTest(edq.testing.unittest.BaseTest):
    """ Test different distance-related functionalities. """

    def test_manhattan_base(self):
        """ Test Manhattan distance and heuristic. """

        test_board = pacai.core.board.load_path('maze-tiny')
        test_state = pacai.core.gamestate.GameState(seed = 4, board = test_board)

        # [(a, b, expected), ...]
        test_cases = [
            # Identity
            (pacai.core.board.Position(0, 0), pacai.core.board.Position(0, 0), 0.0),

            # Lateral
            (pacai.core.board.Position(0, 0), pacai.core.board.Position(1, 0), 1.0),
            (pacai.core.board.Position(0, 0), pacai.core.board.Position(0, 1), 1.0),
            (pacai.core.board.Position(1, 0), pacai.core.board.Position(0, 0), 1.0),
            (pacai.core.board.Position(0, 1), pacai.core.board.Position(0, 0), 1.0),

            # Diagonal
            (pacai.core.board.Position(0, 0), pacai.core.board.Position(1, 1), 2.0),
            (pacai.core.board.Position(1, 1), pacai.core.board.Position(2, 2), 2.0),
            (pacai.core.board.Position(0, 0), pacai.core.board.Position(-1, -1), 2.0),
        ]

        for (i, test_case) in enumerate(test_cases):
            (a, b, expected) = test_case
            with self.subTest(msg = f"Case {i}: {a} vs {b}"):
                distance = pacai.search.distance.manhattan_distance(a, b)
                self.assertAlmostEqual(expected, distance)

                node = pacai.search.position.PositionSearchNode(a)
                problem = pacai.search.position.PositionSearchProblem(
                        test_state,
                        start_position = pacai.core.board.Position(-100, -100),
                        goal_position = b)

                heuristic = pacai.search.distance.manhattan_heuristic(node, problem)
                self.assertAlmostEqual(expected, heuristic)

    def test_euclidean_base(self):
        """ Test Euclidean distance and heuristic. """

        test_board = pacai.core.board.load_path('maze-tiny')
        test_state = pacai.core.gamestate.GameState(seed = 4, board = test_board)

        # [(a, b, expected), ...]
        test_cases = [
            # Identity
            (pacai.core.board.Position(0, 0), pacai.core.board.Position(0, 0), 0.0),

            # Lateral
            (pacai.core.board.Position(0, 0), pacai.core.board.Position(1, 0), 1.0),
            (pacai.core.board.Position(0, 0), pacai.core.board.Position(0, 1), 1.0),
            (pacai.core.board.Position(1, 0), pacai.core.board.Position(0, 0), 1.0),
            (pacai.core.board.Position(0, 1), pacai.core.board.Position(0, 0), 1.0),

            # Diagonal
            (pacai.core.board.Position(0, 0), pacai.core.board.Position(1, 1), 2.0 ** 0.5),
            (pacai.core.board.Position(1, 1), pacai.core.board.Position(2, 2), 2.0 ** 0.5),
            (pacai.core.board.Position(0, 0), pacai.core.board.Position(-1, -1), 2.0 ** 0.5),
        ]

        for (i, test_case) in enumerate(test_cases):
            (a, b, expected) = test_case
            with self.subTest(msg = f"Case {i}: {a} vs {b}"):
                distance = pacai.search.distance.euclidean_distance(a, b)
                self.assertAlmostEqual(expected, distance)

                node = pacai.search.position.PositionSearchNode(a)
                problem = pacai.search.position.PositionSearchProblem(
                        test_state,
                        start_position = pacai.core.board.Position(-100, -100),
                        goal_position = b)

                heuristic = pacai.search.distance.euclidean_heuristic(node, problem)
                self.assertAlmostEqual(expected, heuristic)

    def test_maze_base(self):
        """ Test maze distance. """

        test_board = pacai.core.board.load_path('maze-tiny')
        test_state = pacai.core.gamestate.GameState(seed = 4, board = test_board)

        # Note that the distances will be random because we are using random search.

        # [(a, b, expected), ...]
        test_cases = [
            # Identity
            (pacai.core.board.Position(1, 1), pacai.core.board.Position(1, 1), 0.0),

            # Lateral
            (pacai.core.board.Position(1, 1), pacai.core.board.Position(2, 1), 5.0),
            (pacai.core.board.Position(1, 1), pacai.core.board.Position(1, 2), 1.0),
            (pacai.core.board.Position(2, 1), pacai.core.board.Position(1, 1), 1.0),
            (pacai.core.board.Position(1, 2), pacai.core.board.Position(1, 1), 5.0),

            # Diagonal
            (pacai.core.board.Position(2, 1), pacai.core.board.Position(3, 2), 44.0),
            (pacai.core.board.Position(3, 5), pacai.core.board.Position(4, 4), 78.0),
        ]

        for (i, test_case) in enumerate(test_cases):
            (a, b, expected) = test_case
            with self.subTest(msg = f"Case {i}: {a} vs {b}"):
                distance = pacai.search.distance.maze_distance(a, b, state = test_state)
                self.assertAlmostEqual(expected, distance)

    def test_distanceprecomputer_base(self):
        """ Test precomputing distances. """

        test_board = pacai.core.board.load_path('maze-tiny')
        precomputer = pacai.search.distance.DistancePreComputer()
        precomputer.compute(test_board)

        # [(a, b, expected), ...]
        test_cases = [
            (pacai.core.board.Position(-1, -1), pacai.core.board.Position(-2, -2), None),
            (pacai.core.board.Position(0, 0), pacai.core.board.Position(0, 0), None),

            (pacai.core.board.Position(1, 1), pacai.core.board.Position(1, 2), 1.0),
            (pacai.core.board.Position(1, 1), pacai.core.board.Position(3, 5), 6.0),
            (pacai.core.board.Position(1, 1), pacai.core.board.Position(3, 4), 7.0),
            (pacai.core.board.Position(1, 1), pacai.core.board.Position(4, 4), 6.0),
            (pacai.core.board.Position(1, 1), pacai.core.board.Position(5, 2), 5.0),
            (pacai.core.board.Position(1, 1), pacai.core.board.Position(5, 1), 6.0),

            (pacai.core.board.Position(3, 5), pacai.core.board.Position(4, 4), 2.0),
        ]

        for (i, test_case) in enumerate(test_cases):
            (a, b, expected) = test_case
            with self.subTest(msg = f"Case {i}: {a} vs {b}"):
                distance_forward = precomputer.get_distance(a, b)
                self.assertAlmostEqual(expected, distance_forward)

                distance_backwards = precomputer.get_distance(b, a)  # pylint: disable=arguments-out-of-order
                self.assertAlmostEqual(distance_forward, distance_backwards)
