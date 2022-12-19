import os
import time
from unittest import TestCase

from manafa.services.perfettoService import PerfettoService, device_has_perfetto
from manafa.utils.Utils import execute_shell_command


# python -m unittest  manafa/tests/perfetto/test_perfettoService.py
class TestPerfettoService(TestCase):
    perfetto = PerfettoService()

    def test_start(self):
        res = self.perfetto.start()
        self.assertTrue(res, "perfetto service class starts")
        is_running, _, _ = execute_shell_command("adb shell ps | grep perfetto")
        self.assertEqual(is_running, 0, "perfetto is running")
        self.perfetto.stop()
        self.perfetto.clean()

    def test_stop(self):
        print("testing top")
        self.perfetto.start()
        time.sleep(5)
        res = self.perfetto.stop()
        self.assertRegex(res, r".*.systrace$", "unable to get systrace file")
        self.assertTrue(os.path.exists(res), "systrace file does not exists")
        self.assertGreater(os.stat(res).st_size, 4, "file is empty")
        is_running, _, _ = execute_shell_command("adb shell ps | grep perfetto")
        self.assertNotEqual(is_running, 0, "perfetto is not running after stop")
        self.perfetto.clean()

    def test_export(self):
        self.perfetto.start()
        time.sleep(5)
        self.perfetto.stop()
        res = self.perfetto.export()
        print(f'exported file {res}')
        self.assertTrue(os.path.exists(res), msg='results file exists')
        self.perfetto.clean()

    def test_has_perfetto(self):
        self.assertTrue(device_has_perfetto(), msg="connected Android device has perfetto service")

