from unittest import TestCase

import arena


class TestMain(TestCase):
    def test_main(self):
        """Test application runs without issue on two example files."""
        file1 = '../examples/ww/simple.py'
        file2 = '../examples/ww/random_move.py'
        arena.Arena(["arena", file1, file2, '-n 100']).run()

