import os
from unittest import TestCase

from manafa.parsing.hunter.HunterParser import HunterParser
from manafa.utils.Utils import get_test_resources_dir


class TestHunterParser(TestCase):
    def test_parse_file_new_format(self):
        filepath = os.path.join(get_test_resources_dir(), "example_new_hunter_format.log")
        hp = HunterParser()
        hp.parse_file(filepath)
        self.assertTrue(len(hp.trace) > 1)

    def test_parse_file_old_format(self):
        filepath = os.path.join(get_test_resources_dir(), "example_old_hunter_format.log")
        hp = HunterParser()
        hp.parse_file(filepath)
        self.assertTrue(len(hp.trace) > 1)

    def test_parse_file_both_format(self):
        filepath = os.path.join(get_test_resources_dir(), "example_new_hunter_format.log")
        hp = HunterParser()
        hp.parse_file(filepath)
        self.assertTrue(len(hp.trace) > 1)
        hp.trace = {}
        filepath = os.path.join(get_test_resources_dir(), "example_old_hunter_format.log")
        hp.parse_file(filepath)
        self.assertTrue(len(hp.trace) > 1)

