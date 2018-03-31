from unittest import TestCase

import match


file1 = '../tests/example_codingame_scripts/wonder_women_2f8ed4e.py'
file2 = '../tests/example_codingame_scripts/wonder_women_3d7afe8.py'


class TestMatch(TestCase):
    def setUp(self):
        self.match = match.Match(0,
                                 "mapIndex=1;seed=3268308804",
                                 [file1, file2],
                                 False, False, False)

    def test_init(self):
       pass
