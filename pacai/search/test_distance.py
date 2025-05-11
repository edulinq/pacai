import pacai.core.board
import pacai.search.distance
import pacai.search.position
import pacai.test.base

class DistanceTest(pacai.test.base.BaseTest):
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
