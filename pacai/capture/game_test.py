import os

import edq.testing.unittest
import edq.util.dirent

import pacai.capture.bin

class GameTest(edq.testing.unittest.BaseTest):
    """ Test specifics for capture games. """

    def test_load_randomboard_replay(self):
        """ Test loading a replay that has a random board. """

        temp_dir = edq.util.dirent.get_temp_dir(prefix = 'pacai-test-')
        replay_path = os.path.join(temp_dir, 'test.replay')

        expected_score = -10

        # Run a short capture game and save the replay.
        argv = [
            '--seed', '4',
            '--quiet',
            '--board', 'random-6',
            '--red', 'capture-team-baseline',
            '--blue', 'capture-team-dummy',
            '--ui', 'null',
            '--max-turns', '80',
            '--save-path', replay_path,

        ]
        _, results = pacai.capture.bin.main(argv = argv)

        self.assertEqual(expected_score, results[0].score)

        # Replay the game and get the same result.
        argv = [
            '--quiet',
            '--ui', 'null',
            '--replay-path', replay_path,

        ]
        _, results = pacai.capture.bin.main(argv = argv)

        self.assertEqual(expected_score, results[0].score)
