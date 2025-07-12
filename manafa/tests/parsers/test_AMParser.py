import json
import os
from unittest import TestCase

from manafa.parsing.hunter.AMParser import AMParser
from manafa.parsing.hunter.HunterParser import HunterParser
from manafa.utils.Utils import get_test_resources_dir


class TestHunterParser(TestCase):

    def test_parse_file(self):
        filepath = os.path.join(get_test_resources_dir(), "am_log.csv")
        print(filepath)
        ap = AMParser()
        ap.parse_file(filepath)
        print(json.dumps(ap.trace, indent=2))
        self.assertTrue(len(ap.trace) > 1)