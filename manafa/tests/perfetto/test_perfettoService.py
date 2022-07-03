import os
import time
from unittest import TestCase

from manafa.services.perfettoService import PerfettoService
from manafa.utils.Utils import execute_shell_command


class TestPerfettoService(TestCase):
    perfetto = PerfettoService()

    '''def test_start(self):
        res = self.perfetto.start()
        self.assertTrue(res, "perfetto service failed on start")
        is_running, _, _ = execute_shell_command("adb shell ps | grep perfetto")
        self.assertEqual(is_running, 0, "perfetto was not running")
        self.perfetto.stop()
        self.perfetto.clean()
        

    def test_stop(self):
        self.perfetto.start()
        time.sleep(2)
        res = self.perfetto.stop()
        self.assertRegex(res, r".*.systrace$", "unable to get systrace file")
        self.assertTrue(os.path.exists(res), "systrace file does not exists")
        self.assertGreater(os.stat(res).st_size, 4, "file is empty")
        is_running, _, _ = execute_shell_command("adb shell ps | grep perfetto")
        self.assertNotEqual(is_running, 0, "perfetto still running")
        self.perfetto.clean()'''

    def test_export(self):
        self.perfetto.start()
        time.sleep(1)
        self.perfetto.stop()
        res = self.perfetto.export()
        print(res)
        self.perfetto.clean()


    def test_clean(self):
        self.assertTrue(True)

    def test_full_workflow(self):
        self.assertTrue(True)