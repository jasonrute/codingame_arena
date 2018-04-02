from unittest import TestCase

import arena


class TestMain(TestCase):
    def test_main(self):
        """Test application runs without issue on two example files."""
        file1 = '../tests/example_codingame_scripts/wonder_women_2f8ed4e.py'
        file2 = '../tests/example_codingame_scripts/wonder_women_3d7afe8.py'
        arena.Arena(["arena", file1, file2, '-n 1']).run()

